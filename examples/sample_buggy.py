def two_sum(nums, target):
    # Bug: allows an element to pair with itself.
    for i, a in enumerate(nums):
        for j, b in enumerate(nums):
            if a + b == target:
                return [i, j]
