# CyclicLoadSimulation
Simulation of prestressed concrete beam under cyclic load

## Initialisation

Defintion of the test beam. Every test beam has a specific numnber of strands with a specific number of wires each.
Every wire already underwent fatigue from previous loads before the experiment.

```
nr_wires = 35
nr_strands = 5

mu_fatigue_initial = 400
sigm_fatigue_initial = 100

# inner wires
wires = [Wire(i, True, True, np.random.normal(mu_fatigue_initial, sigm_fatigue_initial)) 
         for i in range(nr_strands)]
# inner strand
wires += [Wire(i, False, True, np.random.normal(mu_fatigue_initial, sigm_fatigue_initial)) 
         for i in range(nr_strands,nr_strands+6)]
# outer strand
wires += [Wire(i, False, True, np.random.normal(mu_fatigue_initial, sigm_fatigue_initial)) 
         for i in range(nr_strands+6,nr_wires)]
```

Definition of the experiment:
```
exp = Experiment(id='SB01', stress_range_0=200, fctm=3.89,
                 nr_wires=nr_wires, nr_strands=nr_strands, 
                 wires=wires)
```

Change of settings (if not specified, defaults will be used):
```
exp.lambda_fatigue = 0.2e-1
exp.lambda_fatigue_fretting_crack = 0.5e1
exp.lambda_fatigue_fretting_stree = 0.5e1
```

## Running an Experiment

In this example, the experiment is stopped when more than 20 wires are broken or after 6 million load cycles.
Every load cycles is simulated:
- A new fatigue value for each wire is assigned
- (New) Broken wires are determined based on fatigue values
- The crack width is determined
- In case a new wire broke, the experiment needs to be updated

```
while (exp.nr_broken < 20) and (exp.nr_cycles < 6e6):
    exp.update_wires()
```
