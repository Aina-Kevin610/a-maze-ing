from mlx import Mlx

if __name__ == "__main__":
    mlx = Mlx()

    mlx_ptr = mlx.mlx_init()
    img = mlx.mlx_new_image(mlx_ptr, 800, 800)
    win = mlx.mlx_new_window(mlx_ptr, 800, 800, "Test")

    data, bpp, size_line, _ = mlx.mlx_get_data_addr(img)

    color = 0x00FFFF

    r = (color >> 16) & 0xFF 
    b = color & 0xFF
    g = (color >> 8) & 0xFF


    x = 20
    y = 50
    offset = (size_line * y) + (x * bpp) // 8
    data[offset] = b
    data[offset + 1] = g
    data[offset + 2] = r
    mlx.mlx_loop()

    # mlx:   BGRT
    # color: RGBA
