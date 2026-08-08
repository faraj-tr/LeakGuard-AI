from leakguard.entropy import calculate_entropy


def test_empty_string_has_zero_entropy():
    assert calculate_entropy("") == 0.0


def test_repeated_character_has_zero_entropy():
    assert calculate_entropy("aaaaaaaaaa") == 0.0


def test_random_like_value_has_higher_entropy():
    simple_value = "aaaaaaaaaaaaaaaaaaaa"

    random_value = "K7mP2xQ9vL4sN8zA1c"

    simple_entropy = calculate_entropy(simple_value)
    random_entropy = calculate_entropy(random_value)

    assert random_entropy > simple_entropy