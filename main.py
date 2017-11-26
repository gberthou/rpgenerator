import model
import lore

my_lore = lore.Lore()
my_scenario = model.Scenario(my_lore, 2, 2, 4, 5, .5)
print(my_scenario.to_dot_format())
