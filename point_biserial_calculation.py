import pandas as pd
import scipy.stats as stats
import sys

def pbc_senticnet_ocean(csv):
    """
        Open a csv containing the data
        and finds the point-biserial correlation
        between each dimension of SenticNet and OCEAN

        input:
        ----------
            - A csv file with data formatted
            the same as data/features_extractor_example.csv

        output:
        ----------
            - A csv file containing the point-biserial correlations
            between SencitNet dimensions and OCEAN
            - A csv file containing the p-values of the above correlations
    """
    
    # Read file
    df = pd.read_csv(csv).dropna()
    
    # Drop useless data
    df = df.drop(df.columns[[0, 1]], axis=1)

    # Dimensions of SenticNet and OCEAN
    stcnet = ['stcnet_attitude', 'stcnet_introspection', 'stcnet_sensitivity', 'stcnet_temper', 'stcnet_polarity']
    ocean  = ['ocean_agreeableness', 'ocean_conscientiousness', 'ocean_extraversion', 'ocean_neuroticism', 'ocean_openness']

    # Result dataframes
    res_df = pd.DataFrame(columns=stcnet, index=ocean)
    pval_df = pd.DataFrame(columns=stcnet, index=ocean)

    # Calculate point biserial correlation
    for oc in ocean:
        for st in stcnet:
            # Calculates rpb
            rpb = stats.pointbiserialr(
                df[oc].to_numpy(),
                df[st].to_numpy()
            )

            # Assign to DataFrame
            res_df[st][oc] = rpb[0]
            pval_df[st][oc] = rpb[1]

    # Export data
    res_df.to_csv("data/rpb_corr.csv")  # correlations
    pval_df.to_csv("data/rpb_pval.csv") # p-values

def main():
    """
        Main
    """
    pbc_senticnet_ocean("data/features_extractor_example.csv")
    

if __name__ == '__main__':
    main()
