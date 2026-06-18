"""
Problem:    Two Sum
Link:       https://leetcode.com/problems/two-sum/
Number:     0001
Topic:      Arrays & Hashing
Difficulty: Easy

---

Problem Statement:
    Given an array of integers nums and an integer target, return indices of
    the two numbers such that they add up to target.

Examples:
    Input:  nums = [2,7,11,15], target = 9
    Output: [0,1]

    Input:  nums = [3,2,4], target = 6
    Output: [1,2]

Constraints:
    - 2 <= nums.length <= 10^4
    - Only one valid answer exists.
"""

from typing import List, Optional


# ---------------------------------------------------------------------------
# Approach 1 -- Brute Force
# Time:  O(n^2)  |  Space: O(1)
# ---------------------------------------------------------------------------

class SolutionBruteForce:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []


# ---------------------------------------------------------------------------
# Approach 2 -- Hash Map  (optimal)
# Time:  O(n)  |  Space: O(n)
# ---------------------------------------------------------------------------

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []


# ---------------------------------------------------------------------------
# Tests  (remove @pytest.mark.skip once your solution is correct)
# ---------------------------------------------------------------------------
import pytest

# -- SolutionBruteForce --

@pytest.mark.skip(reason='not solved yet')
def test_brute_force_example_1():
    assert SolutionBruteForce().twoSum([2, 7, 11, 15], 9) == [0, 1]

@pytest.mark.skip(reason='not solved yet')
def test_brute_force_example_2():
    assert SolutionBruteForce().twoSum([3, 2, 4], 6) == [1, 2]

@pytest.mark.skip(reason='not solved yet')
def test_brute_force_example_3():
    assert SolutionBruteForce().twoSum([3, 3], 6) == [0, 1]

# -- Solution (Hash Map) --

@pytest.mark.skip(reason='not solved yet')
def test_example_1():
    assert Solution().twoSum([2, 7, 11, 15], 9) == [0, 1]

@pytest.mark.skip(reason='not solved yet')
def test_example_2():
    assert Solution().twoSum([3, 2, 4], 6) == [1, 2]

@pytest.mark.skip(reason='not solved yet')
def test_example_3():
    assert Solution().twoSum([3, 3], 6) == [0, 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
