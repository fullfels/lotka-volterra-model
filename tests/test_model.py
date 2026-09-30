import numpy as np

from lotka_volterra import conserved_quantity, equilibrium, simulate


def test_equilibrium_matches_parameters():
    deer, wolves = equilibrium()
    np.testing.assert_allclose(deer, 997.073, rtol=1e-4)
    np.testing.assert_allclose(wolves, 50.717, rtol=1e-4)


def test_simulation_is_positive_and_nearly_conservative():
    time, deer, wolves = simulate(points=600)
    assert len(time) == len(deer) == len(wolves) == 600
    assert np.all(deer > 0)
    assert np.all(wolves > 0)
    invariant = conserved_quantity(deer, wolves)
    assert np.max(np.abs(invariant - invariant[0])) < 1e-5
