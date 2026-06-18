//DEPS org.junit.jupiter:junit-jupiter:5.10.2
//DEPS org.junit.platform:junit-platform-console-standalone:1.10.2
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Problem:    Two Sum
 * Link:       https://leetcode.com/problems/two-sum/
 * Number:     0001
 * Topic:      Arrays & Hashing
 * Difficulty: Easy
 *
 * -------------------------------------------------------------------
 *
 * Problem Statement:
 *   Given an array of integers nums and an integer target, return
 *   indices of the two numbers that add up to target.
 */


// ---------------------------------------------------------------------------
// Approach 1 -- Brute Force
// Time:  O(n^2)  |  Space: O(1)
// ---------------------------------------------------------------------------

class SolutionBruteForce {
    public int[] twoSum(int[] nums, int target) {
        for (int i = 0; i < nums.length; i++)
            for (int j = i + 1; j < nums.length; j++)
                if (nums[i] + nums[j] == target)
                    return new int[]{i, j};
        return new int[]{};
    }
}


// ---------------------------------------------------------------------------
// Approach 2 -- Hash Map  (optimal)
// Time:  O(n)  |  Space: O(n)
// ---------------------------------------------------------------------------

class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (seen.containsKey(complement))
                return new int[]{seen.get(complement), i};
            seen.put(nums[i], i);
        }
        return new int[]{};
    }
}


// ---------------------------------------------------------------------------
// Tests  (remove @Disabled once your solution is correct)
// ---------------------------------------------------------------------------

class SolutionBruteForceTest {
    private final SolutionBruteForce solution = new SolutionBruteForce();

    @Disabled("not solved yet")
    @Test
    void testExample1() {
        assertArrayEquals(new int[]{0, 1}, solution.twoSum(new int[]{2, 7, 11, 15}, 9));
    }

    @Disabled("not solved yet")
    @Test
    void testExample2() {
        assertArrayEquals(new int[]{1, 2}, solution.twoSum(new int[]{3, 2, 4}, 6));
    }

    @Disabled("not solved yet")
    @Test
    void testExample3() {
        assertArrayEquals(new int[]{0, 1}, solution.twoSum(new int[]{3, 3}, 6));
    }
}

class SolutionTest {
    private final Solution solution = new Solution();

    @Disabled("not solved yet")
    @Test
    void testExample1() {
        assertArrayEquals(new int[]{0, 1}, solution.twoSum(new int[]{2, 7, 11, 15}, 9));
    }

    @Disabled("not solved yet")
    @Test
    void testExample2() {
        assertArrayEquals(new int[]{1, 2}, solution.twoSum(new int[]{3, 2, 4}, 6));
    }

    @Disabled("not solved yet")
    @Test
    void testExample3() {
        assertArrayEquals(new int[]{0, 1}, solution.twoSum(new int[]{3, 3}, 6));
    }
}


// JBang entry point -- runs all test classes in this file
class JBangRunner {
    public static void main(String[] args) throws Exception {
        var launcher = org.junit.platform.launcher.core.LauncherFactory.create();
        var request  = org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder
            .request()
            .selectors(
                org.junit.platform.engine.discovery.DiscoverySelectors.selectClass(SolutionBruteForceTest.class),
                org.junit.platform.engine.discovery.DiscoverySelectors.selectClass(SolutionTest.class)
            )
            .build();
        var listener = new org.junit.platform.launcher.listeners.SummaryGeneratingListener();
        launcher.discover(request);
        launcher.execute(request, listener);
        var summary = listener.getSummary();
        summary.printFailuresTo(new java.io.PrintWriter(System.out, true));
        if (summary.getTotalFailureCount() > 0) System.exit(1);
    }
}
