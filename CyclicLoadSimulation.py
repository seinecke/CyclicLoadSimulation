import numpy as np

class Experiment:
    """This class describes the experiment setup. 
    Both the characteristics of a specific experiment and
    of the simulation are included.
    Moreover, the state during a simulation run can be acessed.
    """
    
    def __init__(self, id, nr_wires, nr_strands, stress_range_0, fctm, wires):
        """Initialised the experiment.
        
        Parameters
        -----------
        id: string
            Identifier of the test beam.
        nr_wires: int
            Total number of wires in the test beam.
        nr_strands: int
            Total number of strands.
        stress_range_0: float
            Initial stress range in N/mm2.
        fctm: float
            Concrete tensile strength in MPa.
        wires: wire object
            All wires created with corresponding class.
        
        """
        self.id = id
        self.nr_wires = nr_wires
        self.nr_strands = nr_strands
        self.stress_range_0 = stress_range_0 #[N/mm2]
        self.stress_range = self.stress_range_0 #[N/mm2]
        self.nr_cycles = 0
        self.crack_width = 0 # [mm]
        self.nr_broken = 0
        self.arr = []
        self.fctm = fctm # in MPA
        self.wires = wires
        self.lambda_fatigue_fretting_crack = 5e-7
        self.lambda_fatigue_fretting_stress = 5e-8
        self.lambda_fatigue = 3e-7
        
    def update_wires(self):
        """Method to update all wires.
        Each wire is updated, dependent on the stress range and the crack width.
        In case a wire breaks, the experiment is updated as well 
        (since the number of broken wires influences the current stress range).
        """
        update = False
        self.nr_cycles += 1
        for w in self.wires:
            update_exp = w.update_wire(self.stress_range, 
                                       self.crack_width,
                                       self.lambda_fatigue,
                                       self.lambda_fatigue_fretting_crack, 
                                       self.lambda_fatigue_fretting_stress)
            if update_exp:
                update = True
        if update:
            self.update_experiment(self.nr_cycles)
    
    def update_experiment(self, nr_cycles):
        """Method to update the experiment.
        If a wire broke, the stress range, the number of broken wires, 
        and the crack width needs to be updated. 
        Moreover, the information on the cycle where the wire broke is appended
        to an array for further references, as well as the corresponding crack width.
        """
        self.nr_cycles = nr_cycles
        nr_broken = np.sum([self.wires[i].broken for i in range(self.nr_wires)])
        if self.nr_broken != nr_broken:
            self.nr_broken = nr_broken
            self.stress_range = ( self.nr_wires / (self.nr_wires - self.nr_broken) 
                             * self.stress_range_0 )
            self.crack_width = self.calc_crack_width()
            self.write()
            
    def write(self):
        """Method to append information.
        When called, the number of cycles, the number of broken wires
        and the crack width is noted."""
        self.arr.append([self.nr_cycles, self.nr_broken, self.crack_width])
        
    def calc_crack_width(self):
        """Method to calculate the crack width. 
        The function to calculate it is from SFB823 Discussion Paper Nr.25/2015.
        It's formula (7).
        The used parameters are:
        k_t = 0.6
        E_p = 195e3 MPa
        A_p = 1000 mm2
        
        Returns
        ----------
        crack width: float
            The crack width in mm.
        """
        k_t = 0.6 # no unit
        E_p = 195e3 # [MPa = N/mm2]
        A_p = 1000 # [mm**2] ###10000 #?? # 4.5m x 0.3m = 1.35m2 ?
        A_pn = (1. - self.nr_broken / self.nr_wires) * A_p
        cw = (1. - k_t) * self.stress_range ** 2 * A_pn
        cw = cw / ( 0.72 * np.pi * self.fctm * E_p * np.sqrt(A_pn))
        return cw #[mm]

class Wire:
    """This class describes a single wire.
    Each wire has the information if it is a inner or outer wire,
    and if its strand is an inner or outer strand.
    Moreover, it stores the current fatigue value and if it is broken or not.
    """
    
    def __init__(self, id, inner_wire, inner_strand, fatigue):
        """Initialised a single wire.
        
        Parameters
        -----------
        id: string
            Identifier of the wire.
        inner_wire: bool
            Specifies if it is an inner wire or not.
        inner_strand: bool
            Specifies if it is in an inner strand or not.   
        fatigue: float
            The initial fatigue of a wire.
        """
        self.id = id
        self.inner_wire = inner_wire
        self.inner_strand = inner_strand
        self.fatigue = fatigue
        self.broken = False 
        
    def update_wire(self, stress_range, crack_width, lambda_fatigue, 
                    lambda_fatigue_fretting_crack, lambda_fatigue_stress):
        """This methods updates a single wire.
        The fatigue value of a wire is updated dependent on the stress range
        and the crack width.
        The total fatigue is a sum of the fatigue from stress and from fretting.
        """
        if self.broken == True:
            return False
        else:
            self.fatigue = (self.fatigue 
                            - self.calc_fatigue_exp(
                                                    stress_range, 
                                                    lambda_fatigue
                                                    )
                            - self.calc_fatigue_fretting(
                                                    crack_width,
                                                    stress_range, 
                                                    lambda_fatigue_fretting_crack, 
                                                    lambda_fatigue_stress
                                                    ) 
                           )
            if self.fatigue < 0:
                self.broken = True
                return True
            else:
                return False
            
    def calc_fatigue_fretting(self, 
                              crack_width, 
                              stress_range, 
                              lambda_fatigue_fretting_crack, 
                              lambda_fatigue_fretting_stress):
        """Method to calculate the fretting.
        Fretting does not occur for inner wires and strands.
        Fretting depends on the current stress range and crack width.
        
        Returns
        ---------
        fretting: float
            The fretting for one cycle. 
        """
        if self.inner_strand or self.inner_wire:
            return 0
        else:
            fretting_crack = np.random.exponential(
                lambda_fatigue_fretting_crack * crack_width)
            fretting_stress = np.random.exponential(
                lambda_fatigue_fretting_stress * stress_range)
            return fretting_crack + fretting_stress
           
    def calc_fatigue_exp(self, stress_range, lambda_fatigue):
        """Method to calculate fatigue.
        It depends on the current stress range.
        
        Returns
        ---------
        fatigue: float
            The fatigue for one cycle. 
        """
        return np.random.exponential(lambda_fatigue * stress_range)
