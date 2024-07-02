
import pandas as pd




dataset[['H2S', 'CO2']].mean()
dataset[['H2S', 'CO2']].std()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
          prog = 'Roulette Statistics',
          description = 'Roulette Statistics',
          epilog = '')

    parser.add_argument('fn')
    args = parser.parse_args()

    dataset = pd.read_csv( args.fn )
    cols = dataset.columns

