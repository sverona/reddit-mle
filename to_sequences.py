import pandas as pd


df = pd.read_csv("./comments-data.csv")


def find_best_thread(comment):
    children = df[lambda row: row["parent_id"] == comment["id"]]
    new_comment = pd.DataFrame(comment)
    if not children.empty:
        best_child = children.loc[children["ups"].idxmax()]

        remainder_of_thread = find_best_thread(best_child)
        if remainder_of_thread is None:
            return new_comment
        else:
            return pd.concat([new_comment, remainder_of_thread], axis=1)
    return new_comment


print(df)
roots = df[lambda df: df["depth"] == 0]
max_depth = roots["depth"].max()

sequences = []
n = 0
for idx, root in roots.iterrows():
    thread = find_best_thread(root)
    print(thread)
    print()
    ups = thread.loc["ups"].tolist()
    sequences.append(ups + [0] * (max_depth - len(ups)))

sequence_df = pd.DataFrame(sequences).fillna(0)
print(sequence_df)

sequence_df.to_csv('./comments-sequential.csv')
