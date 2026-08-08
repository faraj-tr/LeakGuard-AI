from leakguard.masking import mask_secret


def test_mask_secret_hides_original_value():
    secret = "LEAKGUARD_FAKE_SECRET_123"

    masked = mask_secret(secret)

    assert masked != secret
    assert secret not in masked


def test_short_secret_is_fully_hidden():
    secret = "12345678"

    masked = mask_secret(secret)

    assert masked == "********"