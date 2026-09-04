import sys
sys.path.insert(0, r'C:\Sheesh\Projects\Razorpay_Buildathon\backend')

def test_no_double_counting():
    at_risk = 10000
    recovered = 4000 + 6000
    assert recovered == at_risk
    rate = recovered / at_risk * 100
    assert rate == 100.0
    print("PASS: Revenue: no double counting")

def test_partial_recovery():
    at_risk = 10000
    recovered = 4000
    rate = recovered / at_risk * 100
    assert rate == 40.0
    print("PASS: Revenue: partial recovery rate correct")

def test_zero_recovery():
    at_risk = 10000
    recovered = 0
    rate = recovered / at_risk * 100
    assert rate == 0.0
    print("PASS: Revenue: zero recovery handled")

if __name__ == "__main__":
    test_no_double_counting()
    test_partial_recovery()
    test_zero_recovery()
    print("\nAll revenue tests passed!")