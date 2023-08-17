from qrplatba import QRPlatbaGenerator


def generate_qr_code(
        account: str,
        amount: float,
        vs: int,
        message: str,
        due_date,
        file_name: str,
        ks: int = None,
        ss: int = None,
):
    generator = QRPlatbaGenerator(
        account=account,
        amount=amount,
        x_vs=vs,
        message=message,
        due_date=due_date,
        x_ks=ks,
        x_ss=ss,
    )
    img = generator.make_image()
    img.save(file_name)
    # # optional: custom box size and border
    # img = generator.make_image(box_size=20, border=4)
    # # optional: get SVG as a string.
    # # Encoding has to be 'unicode', otherwise it will be encoded as bytes
    # svg_data = img.to_string(encoding='unicode')
