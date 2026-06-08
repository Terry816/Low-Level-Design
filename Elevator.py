"""
What is an Elevator System?
An elevator system manages multiple elevators serving different floors in a building. When someone requests an elevator, the system decides which one to dispatch. Once inside, passengers select their destination floors. The system needs to move elevators efficiently while handling multiple concurrent requests.

Requirement:
    -primary capabilities - how many floors? how many elevators? Elevator can go UP or DOWN. System must handle concurrency
    -error handling - what if two people press at same time? Block one request? Only one person's request goes through the other is queued. What if the person tries to choose
    any floor <= the current and they pressed up (do nothing). same for down >= it. 
    -out of scope: Fire emergency, door close/door open, UI rendering, Hardware communication, elevator capacity,

1. Elevator must support 10 floors [0-9] and 3 elevators
2. Elevators can do UP or DOWN.
3. Once inside, if UP -> selected_floor > current_floor 
                if DOWN -> selected_floor < current_floor
4. Efficent algorithm to choose elevator to pick up person (simulate real elevator SCAN behavior)
5. A RequestType is either from OUTSIDE the elevator (UP or DOWN) or INSIDE (can select one or more valid floor)
6. Handle concurrent request
7. going up/down a floor, changing Direction UP -> DOWN, DOWN -> UP, or (UP || DOWN) -> IDLE, and stopping at a floor to complete a request all takes 1 tick of the time

Entities:
    ElevatorController - orchestrator
    Elevator
    Request

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"

class ElevatorController:
    - elevators: List[Elevator]
    - floors: int
    - externalRequests: Set[ExternalRequest]

    + addElevatorRequest(floor, direction: Direction) -> bool
    + step() -> simulate time passes by looping through and updating all the elevator states.


class Elevator:
    - status: Direction
    - current_floor: int
    - requests: Set[InternalRequest] #list of floors currently selected INTERNAL REQUESTS ONLY. Algorithm will determine how to pop from it

    + queueRequest(floor) -> #adds to our queue. will only add to our queue if it is idle or if it is matching the direction of the elevator.
    + if UP - floor > current_floor
    + if DOWN - floor < current_floor
    + step() -> update the current state (either up/down a floor), stop at floor to let people off, or changing status
    + getCurrentFloor() -> current_floor

class Request:
    - direction
    - floor

    + getDirection()
    + getFloor()

class InternalRequest(Request):
    #floor represents the floor they wish to go

class ExternalRequest(Request):
    #floor represents the floor they came from 

SCAN LOGIC

1. Find nearest elevator (same direction) 
    a. If UP -> elevator.current_floor < floor
    b. if DOWN -> elevator.current_floor > floor
    c. return None there are no possible
2. nearest Idle
    a. return None if no possible Idle
3. add to the elevator with the least amount of requests

"""

#edits - internal requests dont need to specify a direction becuase its alreayd going a specific direction

from enum import Enum

class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"
 

class ExternalRequest:
    def __init__(self, floor, direction: Direction) -> None:
        self.floor = floor
        if direction == "IDLE":
            raise Exception("Cannot make an IDLE Request")
        self.direction = direction

class InternalRequest:
    def __init__(self, floor) -> None:
        self.floor = floor


class ElevatorController:
    def __init__(self, elevators=3, floors=10) -> None:
        self.elevators = [Elevator() for _ in range(elevators)]
        self.floors = floors
        self.externalRequests = set()

    def addElevatorRequest(self, floor, direction: Direction) -> bool:
        floor -= 1 # to adjust to index
        if floor < 0 or floor > 9:
            return False
        
        self.externalRequests.add(ExternalRequest(floor, direction))
        return True

    def step(self): #empty out the externalrequests to the necessary elevators
        for e in self.elevators:
            e.step()
        
        for externalReq in self.externalRequests:
            floor, direction = externalReq.floor, externalReq.direction
            elevator = self._findNearestElevator(floor, direction)
            if not elevator:
                elevator = self._findLeastBusyElevator()
            elevator.queueRequest(floor)
            

    def _findNearestElevator(self, floor, direction) -> Elevator | None: #find the nearest elevator going the same direction, or idle
        minDistance = 10
        closestElevator = None
        for e in self.elevators:
            if e.status == direction and e.current_floor < floor:
                minDistance = min(minDistance, abs(e.current_floor - floor))
                closestElevator = e
            elif e.status == direction and e.current_floor > floor:
                minDistance = min(minDistance, abs(e.current_floor - floor))
                closestElevator = e
            elif e.status == "IDLE":
                minDistance = min(minDistance, abs(e.current_floor - floor))
                closestElevator = e
        return closestElevator
    
    def _findLeastBusyElevator(self) -> Elevator:
        minRequests = 11
        leastBusy = self.elevators[0]
        for e in self.elevators:
            if len(e.internalRequests) < minRequests:
                minRequests = len(e.internalRequests)
                leastBusy = e
        return leastBusy
    
class Elevator:
    def __init__(self) -> None:
        self.status = Direction.IDLE
        self.current_floor = 0
        self.internalRequests = set()

    def _isvalidFloor(self, floor) -> bool:
        if floor < 0 or floor > 9:
            return False
        return True

    def queueRequest(self, floor) -> bool:
        if not self._isvalidFloor(floor): return False
        if self.status == "DOWN" and floor >= self.current_floor:
            return False
        elif self.status == "UP" and floor <= self.current_floor:
            return False
        self.internalRequests.add(InternalRequest(floor))
        return True
    
    def step(self):
        pass


    # + step() -> update the current state (either up/down a floor), stop at floor to let people off, or changing status
