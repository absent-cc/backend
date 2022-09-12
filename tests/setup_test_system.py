def generate_ssh_keys(creds_folder="creds"):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    from os.path import exists
    from os import mkdir

    if exists(f"./{creds_folder}/id_rsa") and exists(f"./{creds_folder}/id_rsa.pub"):
        print("SSH keys already exist")
        return

    if not exists(creds_folder):
        mkdir(creds_folder)

    key = rsa.generate_private_key(
        backend=default_backend(), public_exponent=65537, key_size=2048
    )

    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.OpenSSH,
        serialization.NoEncryption(),
    )

    public_key = key.public_key().public_bytes(
        serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
    )

    with open(f"./{creds_folder}/id_rsa", "wb") as f:
        f.write(private_key)

    with open(f"./{creds_folder}/id_rsa.pub", "wb") as f:
        f.write(public_key)


if __name__ == "__main__":
    generate_ssh_keys()  # Generate ssh keys for testing. These keys are completly unsafe and are used for testing only.
