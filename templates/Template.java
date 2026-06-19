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
 *
 * Approach:
 *   HashMap -- store each number's index; on each step check if the
 *   complement (target - num) already exists in the map.
 *
 * Complexity:
 *   Time:  O(n)
 *   Space: O(n)
 */

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


// JBang entry point -- discovers and runs every *Test class in this file,
// printing a per-test PASS / FAIL / SKIP line similar to `pytest -v`.
class JBangRunner {
    public static void main(String[] args) throws Exception {
        var launcher = org.junit.platform.launcher.core.LauncherFactory.create();
        var request  = org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder
            .request()
            .selectors(org.junit.platform.engine.discovery.DiscoverySelectors
                .selectPackage(""))
            .build();

        // Live, per-test output -- prints as each test finishes (PASS / FAIL / SKIP)
        var verbose = new org.junit.platform.launcher.TestExecutionListener() {
            @Override
            public void executionSkipped(
                    org.junit.platform.launcher.TestIdentifier id, String reason) {
                if (id.isTest())
                    System.out.println("SKIP  " + id.getDisplayName() + "  (" + reason + ")");
            }

            @Override
            public void executionFinished(
                    org.junit.platform.launcher.TestIdentifier id,
                    org.junit.platform.engine.TestExecutionResult result) {
                if (!id.isTest()) return;
                switch (result.getStatus()) {
                    case SUCCESSFUL:
                        System.out.println("PASS  " + id.getDisplayName());
                        break;
                    case FAILED:
                        System.out.println("FAIL  " + id.getDisplayName());
                        result.getThrowable().ifPresent(t ->
                            System.out.println("      " + t.getMessage()));
                        break;
                    default:
                        break;
                }
            }
        };

        // Aggregate summary -- printed once at the end
        var summaryListener = new org.junit.platform.launcher.listeners.SummaryGeneratingListener();

        launcher.execute(request, verbose, summaryListener);

        var summary = summaryListener.getSummary();
        System.out.println();
        System.out.println(
            summary.getTestsSucceededCount() + " passed, " +
            summary.getTestsFailedCount()    + " failed, " +
            summary.getTestsSkippedCount()   + " skipped"
        );

        if (summary.getTotalFailureCount() > 0) System.exit(1);
    }
}
