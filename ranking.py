import pandas as pd
import ast

df = pd.read_csv("individualSim.csv")

def run():
    valueList = df.values.tolist()
    viewList = []
    for i in range(len(valueList)):
        rankNumber = 0
        for t in range(len(valueList[i][1])):
            if(t+1 in ast.literal_eval(valueList[i][1])):
                rankNumber += ast.literal_eval(valueList[i][1])[t+1]/(t+1)
        viewList.append([valueList[i][0], rankNumber])
    sortedList = sorted(viewList, key=lambda item: item[1], reverse=True)
    for i in range(len(sortedList)):
        print(f"{i+1}: {sortedList[i][0]} {round(sortedList[i][1],3)}")


if __name__ == "__main__":
    run()