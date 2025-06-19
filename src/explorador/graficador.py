import matplotlib.pyplot as plt

# Read file
data_file = "../../../Desktop/Matchups/MK2/winrates.txt"
with open(data_file) as f:
    lines = f.readlines()

# Parse data
configs = []
values = []
for line in lines:
    config_str, value_str = line.split(':')
    config = tuple(map(float, config_str.strip()[1:-1].split(',')))
    value = float(value_str.strip())
    configs.append(config)
    values.append(value)

# Transpose configs
variables = list(zip(*configs))
nombres = [
	"BONUS_MULTIPLICADOR_OBTENIDO",
	"OBTENER_MULTIPLICADOR",
	"ARRANCAR_COLECCIONABLE",
	"VALOR_BASE_PRIMER_CARTA_DUO",
	"BONUS_COMPLETAR_DUO",
	"VALOR_BASE_SIRENA"
]

# Plot scatter plots
num_vars = len(variables)
fig, axs = plt.subplots(3, 2, figsize=(6, 2 * num_vars), tight_layout=True)

print(axs)


for i, var in enumerate(variables):
    axs[i // 2][i % 2].scatter(var, values, alpha=0.7)
    axs[i // 2][i % 2].set_xlabel(f'{nombres[i]}')
    axs[i // 2][i % 2].set_ylabel('Winrate')

plt.show()