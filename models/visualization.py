import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import itertools
import numpy as np


class Visualization:
    def __init__(self, simulation_data):
        self.data = simulation_data
        self.dataframe = pd.DataFrame(simulation_data)

    def plot_stock(self, stock_name, interval):
        plt.figure()
        plt.plot(
            self.data["time"][:interval],
            self.data[stock_name][:interval],
            label=stock_name,
        )
        plt.xlabel("Time")
        plt.ylabel("Quantity")
        plt.title(f"Stock of {stock_name} over Time")
        plt.legend()
        plt.show()

    def plot_flow(self, flow_name, interval):
        plt.figure()
        plt.plot(
            self.data["time"][:interval],
            self.data[flow_name][:interval],
            label=flow_name,
        )
        plt.xlabel("Time")
        plt.ylabel("Rate")
        plt.title(f"Flow Rate of {flow_name} over Time")
        plt.legend()
        plt.show()

    def plot_population_over_time(self, stocks, interval):
        plt.figure()
        for stock in stocks:
            plt.plot(
                self.data["time"][:interval],
                self.data[stock][:interval],
                label=f"{stock.capitalize()} Population",
            )
        plt.xlabel("Time")
        plt.ylabel("Populations")
        plt.title("Population Over Time")
        plt.legend()
        plt.show()

    def plot_phase_diagram(self, stock_1, stock_2, interval):
        plt.figure()
        plt.plot(
            self.data[stock_1][:interval],
            self.data[stock_2][:interval],
            label="Phase Diagram",
        )
        plt.xlabel(f"{stock_1.capitalize()} Population")
        plt.ylabel(f"{stock_2.capitalize()} Population")
        plt.title(f"{stock_1.capitalize()} vs {stock_2.capitalize()} Phase Diagram")
        plt.legend()
        plt.show()

    def plot_hist(self, stock_or_flow, interval):
        plt.figure()
        plt.hist(self.data[stock_or_flow][:interval], bins=20, alpha=0.7)
        plt.xlabel(stock_or_flow.capitalize())
        plt.ylabel("Frequency")
        plt.title(f"Histogram of {stock_or_flow.capitalize()}")
        plt.show()

    def plot_stacked_bar(self, stock_1, stock_2, interval):
        df = self.dataframe[["time", stock_1, stock_2]][:interval]
        df.set_index("time", inplace=True)
        ax = df.plot(kind="bar", stacked=True)
        # Pour éviter l'encombrement de l'axe des x
        n = interval / 5
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % n != 0:
                label.set_visible(False)

        # Rotation des étiquettes pour les rendre lisibles
        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Quantity")
        plt.title("Stacked Bar Chart of Stocks Over Time")
        plt.show()

    def plot_box_plot(self, stock_1, stock_2, interval):
        df = self.dataframe[[stock_1, stock_2]][:interval]
        sns.boxplot(data=df)
        plt.title("Box plot of Stocks")
        plt.ylabel("Quantity")
        plt.show()

    def plot_sensitivity_results(
        self, sensitivity_results, stock_names, flow_names=None
    ):
        # Créez une palette de couleurs
        color_cycle = itertools.cycle(
            ["blue", "green", "red", "purple", "orange", "brown"]
        )

        # Générez une couleur pour chaque ensemble de paramètres
        colors = {params: next(color_cycle) for params in sensitivity_results.keys()}

        # Préparez la figure et les axes
        fig, ax = plt.subplots(figsize=(10, 6))

        # Tracez les données pour chaque ensemble de paramètres
        for params, df in sensitivity_results.items():
            for stock_name in stock_names:
                ax.plot(
                    df["time"],
                    df[stock_name],
                    label=f"{stock_name} at {params}",
                    color=colors[params],
                    marker="o",
                )
            if flow_names:
                for flow_name in flow_names:
                    ax.plot(
                        df["time"],
                        df[flow_name],
                        label=f"{flow_name} at {params}",
                        color=colors[params],
                        linestyle="--",
                    )

        # Réglages des axes et affichage
        ax.set_xlabel("Time")
        ax.set_ylabel("Quantity")
        ax.set_title("Simulation Results for Different Parameters")
        ax.legend()
        plt.show()

    def plot_sensitivity_heatmap(
        self,
        sensitivity_results,
        param_names,
        stock_name,
        aggfunc="mean",
        aggfunc_name="Mean",
        title=None,
    ):
        # Créer une liste pour les données de la heatmap, en agrégeant si nécessaire
        heatmap_data = []
        for params, data in sensitivity_results.items():
            # Assurez-vous que data[stock_name] est une Series Pandas pour appliquer l'agrégation
            if not isinstance(data[stock_name], pd.Series):
                data_series = pd.Series(data[stock_name])
            else:
                data_series = data[stock_name]

            # Appliquer la fonction d'agrégation en utilisant une chaîne de caractères
            agg_value = data_series.agg(aggfunc)
            heatmap_data.append(params + (agg_value,))

        # Convertir en DataFrame
        columns = list(param_names) + [f"{aggfunc_name} Value"]
        heatmap_df = pd.DataFrame(heatmap_data, columns=columns)

        # Grouper et pivoter pour la heatmap
        heatmap_pivot = heatmap_df.pivot(
            index=param_names[0], columns=param_names[1], values=f"{aggfunc_name} Value"
        )

        # Créer et afficher la heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_pivot, annot=True, fmt=".1f", cmap="YlGnBu")
        plt.title(
            title
            or f"Impact of {param_names[0]} and {param_names[1]} on {aggfunc_name} {stock_name}"
        )
        plt.ylabel(param_names[0])
        plt.xlabel(param_names[1])
        plt.show()

    def plot_grid(self, simulation_results, plot_columns, title=None):
        # Identifier le nombre de lignes et de colonnes nécessaires
        params_list = list(simulation_results.keys())
        num_rows = len(set(p[0] for p in params_list))
        num_columns = len(set(p[1] for p in params_list))

        # Créer la grille de sous-graphiques
        fig, axes = plt.subplots(num_rows, num_columns, figsize=(20, 15))
        axes = np.array(axes).reshape(num_rows, num_columns)

        # Tracer les graphiques pour chaque combinaison de paramètres
        for idx, params in enumerate(params_list):
            row, col = divmod(idx, num_columns)
            ax = axes[row, col]
            df = simulation_results[params]

            for column in plot_columns:
                ax.plot(df["time"], df[column], label=column)

            ax.set_title(f"Params: {params}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Quantity")
            ax.legend()

        # Ajuster l'espacement et définir le titre principal
        fig.suptitle(title or "Grid of Subplots")
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def plot_elasticities(self, elasticities, title="Elasticities of Parameters"):
        params, values = zip(*elasticities.items())
        plt.bar(range(len(params)), values)
        plt.xticks(range(len(params)), params)
        plt.ylabel("Elasticity")
        plt.title(title)
        plt.show()
