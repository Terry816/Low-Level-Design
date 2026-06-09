"""
What is an Elevator System?
An elevator system manages multiple elevators serving different floors in a building. When someone requests an elevator, the system decides which one to dispatch. Once inside, passengers select their destination floors. The system needs to move elevators efficiently while handling multiple concurrent requests.

Requirements:
1. System manages 3 elevators serving 10 floors (0-9)
2. Users can request an elevator from any floor (hall call). System decides which elevator to dispatch.
3. Once inside, users can select one or more destination floors
4. Simulation runs in discrete time steps (e.g., a `step()` or `tick()` call advances time)
5. Elevator stops come in two types:
    - Hall calls: Request from a floor with direction (UP or DOWN)
    - Destination: Request from inside elevator (no direction specified)
6. System handles multiple concurrent pickup requests across floors
7. Invalid requests should be rejected (return false)
    - Non-existent floor numbers
8. Requests for the current floor are treated as a no-op / already served (doors out of scope)

Out of scope:
- Weight capacity and passenger limits
- Door open/close mechanics
- Emergency stop functionality
- Dynamic floor/elevator configuration
- UI/rendering layer

Entities:
    ElevatorController - orchestrator
    Elevator
    Request

class ElevatorController:
    - elevators: List<Elevator>

    + ElevatorController()
    + requestElevator(floor, type) -> boolean scan logic to insert it the elevator based on criteria
    + step() -> void

class Elevator:
    - currentFloor: int
    - direction: Direction        // UP, DOWN, IDLE
    - requests: Set<Request>

    + Elevator()
    + addRequest(request) -> boolean
    + step() -> void        order of steps to perform based on priority
    + getCurrentFloor() -> int
    + getDirection() -> Direction

class Request:
    - floor: int
    - type: RequestType

    + Request(floor, type)
    + getFloor() -> int
    + getType() -> RequestType

enum Direction:
    UP
    DOWN
    IDLE

enum RequestType:
    PICKUP_UP
    PICKUP_DOWN
    DESTINATION

SCAN LOGIC

1. Find nearest elevator (same direction) 
    a. If UP -> elevator.current_floor < floor
    b. if DOWN -> elevator.current_floor > floor
    c. return None there are no possible
2. nearest Idle
    a. return None if no possible Idle
3. add to the elevator with the least amount of requests

Priority 1: find_committed_to_floor (The Hitchhiker Method)
It looks for an elevator that is already moving in the requested direction, hasn't passed the requesting floor yet, and has other stops at or beyond that floor.

Example: You are on floor 4 and want to go UP. Elevator A is on floor 2 heading UP to floor 7. It will assign this to Elevator A because it can easily scoop you up on its way.

Priority 2: find_nearest_idle (The Lazy Method)
If no moving elevator can efficiently pick you up, it looks for an elevator that is doing absolutely nothing (Direction.IDLE). It checks all idle elevators and assigns the one physically closest to you.

Priority 3: find_nearest (The Fallback)
If all elevators are busy and moving away from you, it assigns your request to whichever elevator is currently closest in absolute distance, regardless of what direction it is going. You might have to wait for it to finish its current trip, but your request won't be dropped.



step (time) logic - elevator makes one decision here it is

Check for an Empty Queue:
If self.requests is empty, there is nowhere to go. It sets the direction to IDLE and stops doing anything.

Wake Up (if IDLE):
If the elevator is IDLE but suddenly does have requests, it needs to pick a direction. It finds the request that is physically closest to its current floor and sets its direction (UP or DOWN) toward that request.

Check for Stops (Drop-offs and Pickups):
Before moving, it checks if it needs to open its doors on the current floor. It creates dummy variables for a "pickup" (matching its current direction) and a "destination" (someone getting off). If either exists in its queue, it removes them (simulating opening the doors and letting people in/out).

Check the Road Ahead:
It calls has_requests_ahead(). If it is going UP, but there are no more requests above it, it realizes it needs to turn around. It flips its direction to DOWN (or vice versa).

Move:
Finally, if it hasn't stopped to open doors, and it knows what direction it is facing, it physically moves. It increments current_floor += 1 if going UP, or decrements current_floor -= 1 if going DOWN.


"""
from enum import Enum

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"

class RequestType:
    PICKUP_UP = 0
    PICKUP_DOWN = 1
    DESTINATION = 2 

class Request:
    def __init__(self, floor: int, type: int) -> None:
        self.floor = floor
        self.type = type
    
    def getFloor(self):
        return self.floor
    
    def getType(self):
        return self.type

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Request):
            return False
        return self.floor == value.floor and self.type == value.type

    # REQUIRED for placing custom objects into a Python set()
    def __hash__(self):
        return hash((self.floor, self.type))

class Elevator:
    def __init__(self) -> None:
        self.current_floor = 0
        self.direction = Direction.IDLE
        self.requests = set()

    def addRequest(self, request: Request):
        self.requests.add(request) # Fixed typo: changed self.requests to request

    def getCurrentFloor(self):
        return self.current_floor
    
    def _find_nearest_floor(self):
        minDistance = 10
        best = self.current_floor
        for req in self.requests:
            floor = req.floor
            dist = abs(self.current_floor - floor)
            if dist < minDistance:
                best = floor
                minDistance = dist
        return best

    def step(self):
        # ==========================================
        # GROUP 1: BRAIN TASKS (Can all happen at once)
        # ==========================================
        
        # 1. Sleep Check
        if not self.requests:
            self.direction = Direction.IDLE
            return
        
        # 2. Wake Up Check
        if self.direction == Direction.IDLE:
            nearest_floor = self._find_nearest_floor()
            self.direction = Direction.UP if nearest_floor > self.current_floor else Direction.DOWN
            
        # 3. Turnaround Check (Check the road ahead)
        if not self._has_requests_ahead():
            self.direction = Direction.DOWN if self.direction == Direction.UP else Direction.UP

        # ==========================================
        # GROUP 2: BODY TASKS (Only ONE happens per tick)
        # ==========================================
        
        # Determine what kind of hallway pickup matches our current direction
        pickup_type = RequestType.PICKUP_UP if self.direction == Direction.UP else RequestType.PICKUP_DOWN
        
        # Look to see if anyone needs to get on/off at the exact floor we are currently on
        needs_to_open_doors = any(
            req.floor == self.current_floor and req.type in (RequestType.DESTINATION, pickup_type)
            for req in self.requests
        )

        # The Elevator must choose Option A or Option B:
        if needs_to_open_doors:
            # OPTION A: Open Doors (Consumes the tick)
            fulfilled_requests = {
                req for req in self.requests 
                if req.floor == self.current_floor and req.type in (RequestType.DESTINATION, pickup_type)
            }
            self.requests -= fulfilled_requests # Clear them from the queue
            
        else:
            # OPTION B: Move (Consumes the tick)
            if self.direction == Direction.UP:
                self.current_floor += 1
            elif self.direction == Direction.DOWN:
                self.current_floor -= 1

    def _has_requests_ahead(self):
        """Helper method for the Turnaround Check"""
        for req in self.requests:
            if self.direction == Direction.UP:
                if req.floor > self.current_floor:
                    return True
                if req.floor == self.current_floor and req.type in (RequestType.PICKUP_UP, RequestType.DESTINATION):
                    return True
                    
            elif self.direction == Direction.DOWN:
                if req.floor < self.current_floor:
                    return True
                if req.floor == self.current_floor and req.type in (RequestType.PICKUP_DOWN, RequestType.DESTINATION):
                    return True
                    
        return False


class ElevatorController:
    def __init__(self, elevators=3) -> None:
        self.elevators = [Elevator() for _ in range(elevators)]

    def requestElevator(self, floor: int, type: int) -> bool:
        # Removed the `floor -= 1` normalization bug
        if floor < 0 or floor > 9:
            return False
        if type == RequestType.DESTINATION:
            return False
        
        req = Request(floor, type)
        
        # Option 1: Hitchhike
        best = self._hitchhike(floor, type)
        if best:
            best.addRequest(req)
            return True # Added return to prevent waterfall bug
        
        # Option 2: Find nearest Idle
        nearest_idle = self._find_nearest_idle(floor)
        if nearest_idle:
            nearest_idle.addRequest(req)
            return True # Added return to prevent waterfall bug

        # Option 3: Fallback. Assign to the nearest elevator
        nearest_elevator = self._find_nearest_option(floor)
        nearest_elevator.addRequest(req)
        
        return True


    def _hitchhike(self, floor, type):
        minDistance = 10
        best = None
        for e in self.elevators:
            if type == RequestType.PICKUP_UP and e.current_floor < floor:
                dist = abs(e.current_floor - floor)
                if dist < minDistance:
                    best = e
                    minDistance = dist
            elif type == RequestType.PICKUP_DOWN and e.current_floor > floor:
                dist = abs(e.current_floor - floor)
                if dist < minDistance:
                    best = e
                    minDistance = dist
        return best

    def _find_nearest_idle(self, floor):
        minDistance = 10
        best = None
        for e in self.elevators:
            if e.direction == Direction.IDLE:
                dist = abs(e.current_floor - floor)
                if dist < minDistance:
                    best = e
                    minDistance = dist
        return best

    def _find_nearest_option(self, floor):
        minDistance = 10
        best = self.elevators[0]
        for e in self.elevators:
            dist = abs(e.current_floor - floor)
            if dist < minDistance:
                best = e
                minDistance = dist
        return best

    def step(self):
        for e in self.elevators:
            e.step()