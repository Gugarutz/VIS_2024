import numpy as np

class Model:
    def __init__(self, iniState):
        self.state = iniState

    def get_state(self):
        return self.state
    
    def set_state(self, new_state):
        self.state = new_state

    def dydt(self, t, y):
        """Defines the system's dynamics: computes the derivative of the state vector."""
        raise NotImplementedError("This method should be implemented by subclasses.")


class SingleMassOscillator(Model):
    def __init__(self, iniState, m, k, d):
        super().__init__(iniState)
        #your implementation here
        self.__m__ = m      # mass
        self.__k__ = k      # stiffness
        self.d = 2*d*np.sqrt(self.__k__/self.__m__)


    def dydt(self, t):
        """Compute the derivatives of the state (velocity and acceleration)."""
        #----------------------------------------------------------------------------
        #  | implementation here  |
        # \ /                    \ /
        #  v                      v
        position = self.state[0]
        velocity = self.state[1]
        acceleration = 0.        
        
        return np.array([velocity, acceleration]) 
        #----------------------------------------------------------------------------

