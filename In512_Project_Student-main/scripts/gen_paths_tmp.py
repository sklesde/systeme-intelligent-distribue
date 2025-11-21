width, height = 35, 30
x_min, x_max = 2, 32
y_top, y_bottom = 2, 27

band_centers_left = [3, 10, 17]
band_centers_right = [31, 24, 17]


def zigzag_vertical(start_x, start_y, upwards=True, first_dir="right"):
    path = []
    x, y = start_x, start_y
    path.append((x, y))
    dir = first_dir
    while True:
        moved = False
        for _ in range(2):
            if upwards:
                dx = 1 if dir == "right" else -1
                dy = -1
            else:
                dx = 1 if dir == "right" else -1
                dy = 1
            nx, ny = x + dx, y + dy
            # stop if leaving vertical bounds
            if ny < y_top or ny > y_bottom:
                return path
            # also don't go outside global bounds
            if nx < x_min or nx > x_max:
                return path
            x, y = nx, ny
            path.append((x, y))
            moved = True
        dir = "left" if dir == "right" else "right"
        if not moved:
            break
    return path


list_left = []

# left band 0: center 3, start bottom-left of band
cx = band_centers_left[0]
start_x = cx - 1
start_y = y_bottom
list_left.extend(zigzag_vertical(start_x, start_y, upwards=True, first_dir="right"))

# next bands on left: start at top and go downwards
for cx in band_centers_left[1:]:
    last_x, last_y = list_left[-1]
    target_x = cx - 1
    target_y = y_top
    # move vertically to target_y
    while last_y > target_y:
        last_y -= 1
        list_left.append((last_x, last_y))
    while last_y < target_y:
        last_y += 1
        list_left.append((last_x, last_y))
    # move horizontally to target_x
    step = 1 if target_x > last_x else -1
    while last_x != target_x:
        last_x += step
        list_left.append((last_x, last_y))
    # now zigzag downwards
    list_left.extend(zigzag_vertical(last_x, last_y, upwards=False, first_dir="right"))


list_right = []

# right band 0: center 27, start bottom-right of band
cx = band_centers_right[0]
start_x = cx + 1
start_y = y_bottom
list_right.extend(zigzag_vertical(start_x, start_y, upwards=True, first_dir="left"))

for cx in band_centers_right[1:]:
    last_x, last_y = list_right[-1]
    target_x = cx + 1
    target_y = y_top
    while last_y > target_y:
        last_y -= 1
        list_right.append((last_x, last_y))
    while last_y < target_y:
        last_y += 1
        list_right.append((last_x, last_y))
    step = 1 if target_x > last_x else -1
    while last_x != target_x:
        last_x += step
        list_right.append((last_x, last_y))
    list_right.extend(zigzag_vertical(last_x, last_y, upwards=False, first_dir="left"))


print("list_1 =", list_left)
print("list_2 =", list_right)
