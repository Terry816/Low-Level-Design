"""
Design a locker system like Amazon Locker where delivery drivers can deposit packages and customers can pick them up using a code.

Requirements:
1. Carrier deposits a package by specifying size (small, medium, large)
   - System assigns an available compartment of matching size
   - Opens compartment and returns access token, or error if no space
2. Upon successful deposit, an access token is generated and returned
   - One access token per package
3. User retrieves package by entering access token
   - System validates code and opens compartment
   - Throws specific error if code is invalid or expired
4. Access tokens expire after 7 days
   - Expired codes are rejected if used for pickup
   - Package remains in compartment until staff removes it
5. Staff can open all expired compartments to manually handle packages
   - System opens all compartments with expired tokens
   - Staff physically removes packages and returns them to sender
6. Invalid access tokens are rejected with clear error messages
   - Wrong code, already used, or expired - user gets specific feedback

Out of scope:
- How the package gets to the locker (delivery logistics)
- How the access token reaches the customer (SMS/email notification)
- Lockout after failed access token attempts
- UI/rendering layer
- Multiple locker stations
- Payment or pricing


Entities:
LockerController - orchestrator
Token

don't need user. user just gives code
#hashmap - O(1) lookup of the packages.
#cannot use list or LL because lookup is O(n) and the locker system is going to do constant lookups/removals
#cleanup - O(nllogn) better to put O(n) longer time on cleanup than the customer code lookup because much more lookups than cleanups

#len of each hashmap is the # of compartments in use
#

class Locker:
    - compartments: Compartment[]
    - accessTokenMapping: Map<string, AccessToken>

    + Locker(compartments)
    + depositPackage(size) -> string | error
    + pickup(tokenCode) -> void | error
    + openExpiredCompartments() -> void

class AccessToken:
    - code: string
    - expiration: timestamp
    - compartment: Compartment

    + AccessToken(code, expiration, compartment)
    + isExpired() -> boolean
    + getCompartment() -> Compartment
    + getCode() -> string

class Compartment:
    - size: Size
    - occupied: boolean

    + Compartment(size)
    + getSize() -> Size
    + isOccupied() -> boolean
    + markOccupied() -> void
    + markFree() -> void
    + open() -> void

enum Size:
    SMALL
    MEDIUM
    LARGE
    

"""
from enum import Enum
import time

class Size(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

class OutofSpaceError(Exception):
    pass

class InvalidCodeError(Exception):
    pass

class ExpiredTokenError(Exception):
    pass

import threading 

class Locker:
    def __init__(self, small=30, medium=10, large=5) -> None:
        self.small = small
        self.medium = medium
        self.large = large

        self.compartments = []
        for _ in range(small):
            self.compartments.append(Compartment(Size.SMALL))
        for _ in range(medium):
            self.compartments.append(Compartment(Size.MEDIUM))
        for _ in range(large):
            self.compartments.append(Compartment(Size.LARGE))

        self.accessTokenMapping = {} # code : AccessToken
        self.counter = 0 #counter is going to mimic the code generator

        self.lock = threading.Lock()

    def _updateSizes(self, size, increment: bool):
        delta = 1
        if not increment:
            delta = -1

        if size == Size.SMALL:
            self.small += delta
        elif size == Size.MEDIUM:
            self.medium += delta
        else:
            self.large += delta

    def depositPackage(self, size: Size):
        with self.lock:

            if (size == Size.SMALL and self.small == 0) or (size == Size.MEDIUM and self.medium == 0) or (size == Size.LARGE and self.large == 0):
                raise OutofSpaceError(f"Out of lockers of this size: {size}")
        
            self._updateSizes(size, False)

            compartment = None
            for comp in self.compartments:
                if comp.size == size and not comp.isOccupied():
                    compartment = comp
                    break

            if not compartment:
                return None
            compartment.markOccupied()
            self.accessTokenMapping[self.counter] = AccessToken(self.counter, int(time.time()), compartment)
            self.counter += 1
            return self.counter -1

    def pickup(self, tokenCode: int):
        if tokenCode not in self.accessTokenMapping:
            raise InvalidCodeError("Invalid Code used. Please Try Again")
        
        access_token = self.accessTokenMapping[tokenCode]

        if access_token.isExpired():
            raise ExpiredTokenError("Token is Expired. Please come back later")
        
        with self.lock:
            compart = access_token.compartment
            size = compart.size
            del self.accessTokenMapping[tokenCode]
            
            self._updateSizes(size, True)
            compart.markFree()

    def openExpiredCompartments(self):
        with self.lock:
            for code, access_token in list(self.accessTokenMapping.items()):
                if access_token.isExpired():
                    compart = access_token.compartment
                    size = compart.getSize()
                    compart.markFree()
                    self._updateSizes(size, True)
                    del self.accessTokenMapping[code]


class AccessToken:
    def __init__(self, code: int, expiration: int, compartment: Compartment) -> None:
        self.code = code
        self.expiration = expiration
        self.compartment = compartment

    def getCode(self):
        return self.code
    
    def getCompartment(self):
        return self.compartment
    
    def isExpired(self):
        # 7 day. 3600 * 24 * 7
        return True if self.expiration <= (int(time.time()) - (3600*24*7)) else False

class Compartment:
    def __init__(self, size) -> None:
        self.size = size
        self.occupied = False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Compartment):
            return False
        return self.size == other.size and self.occupied == other.occupied

    def getSize(self):
        return self.size

    def isOccupied(self):
        return self.occupied
    
    def markOccupied(self):
        self.occupied = True

    def markFree(self):
        self.occupied = False