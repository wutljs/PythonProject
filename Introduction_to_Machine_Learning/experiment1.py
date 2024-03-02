from sklearn.datasets import load_digits
import numpy as np


def get_feature(img):
    rowSize = 2
    result = np.zeros((4, 4), dtype=np.float64)

    for n in range(4):
        r1 = n * rowSize
        r2 = (n + 1) * rowSize

        for m in range(4):
            c1 = m * rowSize
            c2 = (m + 1) * rowSize
            result[n, m] = np.sum(img[r1:r2, c1:c2]) / (rowSize * rowSize)

    return result.reshape((1, 16))


print('电信2101娄倞硕--0122109360319')
digits, targets = load_digits(return_X_y=True)
print(len(digits))

digits_dict = {0: [], 1: [], 2: [], 3: [],
               4: [], 5: [], 6: [], 7: [],
               8: [], 9: []}

for item, label in zip(digits, targets):
    img = item.reshape((8, 8))
    # f = np.sum(img, axis=1)
    f = get_feature(img)
    digits_dict.get(label).append(f)

for (k, v) in digits_dict.items():
    print(k, ':', len(v))

print(digits_dict.get(0)[0])
