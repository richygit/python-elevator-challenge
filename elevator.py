from __future__ import print_function
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

UP = 1
DOWN = 2
FLOOR_COUNT = 6

class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    """

    def __init__(self):
        self.callbacks = None
        size = FLOOR_COUNT+1
        up = [None] * size
        down = [None] * size
        self.called = [None, up, down]
        self.selected = [None] * size
        #set when motor not moving to indicate the service direction
        self.movement_direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        eprint('## Floor called: ' , floor , ',direction: ' , direction , ', current: ' , self.current_floor())
        self.record_call(floor, direction)
        self.move_check()

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        eprint( '## Floor selected: ' , floor , ', current: ' , self.current_floor())

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        eprint( '## Floor change: ' , self.current_floor())
        self.move_check()

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        eprint( '## Ready: ' , self.current_floor())
        self.move_check()


        ########################

    def not_moving(self):
        return self.movement_direction == None and self.callbacks.motor_direction == None

    def opposite(self, direction):
        if direction == UP:
            return DOWN
        else:
            return UP

    def relative_direction(self, floor):
        if self.current_floor() < floor:
            return UP
        elif self.current_floor() > floor:
            return DOWN
        else:
            return None

    def current_floor(self):
        return self.callbacks.current_floor

    def is_current_call_in_same_direction(self, direction):
        return self.called[direction][self.current_floor()] and self.callbacks.motor_direction == direction

    def is_current_call_in_opposite_direction(self):
        if self.callbacks.motor_direction == UP:
            return self.called[DOWN][self.current_floor()] 
        else:
            return self.called[UP][self.current_floor()] 

    def clear_current_call_in_opposite_direction(self):
        if self.callbacks.motor_direction == UP:
            self.called[DOWN][self.current_floor()] = None
        else:
            self.called[UP][self.current_floor()] = None

    def more_requests_in_current_direction(self):
        return self.more_requests_in_direction(self.callbacks.motor_direction)

    def more_requests_in_direction(self, direction):
        if direction == UP:
            return self.list_idx(self.called[UP][self.current_floor():]) or \
                self.list_idx(self.called[DOWN][self.current_floor():]) or \
                self.list_idx(self.selected[self.current_floor():])
        elif self.callbacks.motor_direction == DOWN:
            return self.list_idx(self.called[UP][:self.current_floor()]) or \
                self.list_idx(self.called[DOWN][:self.current_floor()]) or \
                self.list_idx(self.selected[:self.current_floor()])

    def final_request_in_current_direction(self):
        if self.not_moving():
            return False
        else:
            return not self.more_requests_in_current_direction()


    def should_stop(self):
        return self.is_current_call_in_same_direction(UP) or \
            self.is_current_call_in_same_direction(DOWN) or \
            self.final_request_in_current_direction() or \
            self.selected[self.current_floor()]

    """ returns the index of the first True elem in the 'called' array for the given direction
    """
    def called_idx(self, direction):
        return self.list_idx(self.called[direction])

    def list_idx(self, lst):
        for i, j in enumerate(lst):
            if j:
                return i
        return None

    def next_request_direction(self):
        #TODO this only services calls, not selections
        up = self.called_idx(UP)
        if up:
            return self.relative_direction(up)
        down = self.called_idx(DOWN)
        if down:
            return self.relative_direction(down)

    """ returns the movement direction """
    def clear_current_request(self):
        if self.selected[self.current_floor()]:
            self.selected[self.current_floor()] = None
            if self.more_requests_in_current_direction():
                return self.callbacks.motor_direction
            else:
                return self.next_request_direction()
        elif self.is_current_call_in_same_direction(DOWN):
            self.called[DOWN][self.current_floor()] = None
            return self.callbacks.motor_direction
        elif self.is_current_call_in_same_direction(UP):
            self.called[UP][self.current_floor()] = None
            return self.callbacks.motor_direction
        elif not self.more_requests_in_current_direction():
            if self.is_current_call_in_opposite_direction():
                self.clear_current_call_in_opposite_direction()
                return self.opposite(self.callbacks.motor_direction)
            elif self.more_requests_in_direction(self.opposite(self.callbacks.motor_direction)):
                return self.opposite(self.callbacks.motor_direction)
                


    def direction_to_move(self):

        if self.should_stop():
            self.movement_direction = self.clear_current_request()
            return None
        else:
            return self.next_request_direction()

    def record_call(self, floor, direction):
        if(self.callbacks.current_floor == floor):
            return
        self.called[direction][floor] = True

    def set_motor_direction(self,direction):
        if direction != None:
            self.movement_direction = None
        eprint('## motor set: ', direction)
        self.callbacks.motor_direction = direction

    def move_check(self):
        self.set_motor_direction(self.direction_to_move())
