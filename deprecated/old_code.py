def calculate_rotation_amplitude(midline_curve, full_curve):
    x_vals = []
    amplitudes = []
    print(midline_curve.x_vec, midline_curve.y_vec)
    for index in range(midline_curve.range):
        if not index%2 == 0 and not (index + 1) >= midline_curve.range:
            left_x = index - 1
            right_x = index + 1
            dx = midline_curve.x_vec[right_x] - midline_curve.x_vec[left_x]
            dy = midline_curve.y_vec[right_x] - midline_curve.y_vec[left_x]
            #print(dy/dx)
            slope = dy/dx
            inv_slope = -1/slope
            if inv_slope > 0:
                x_step_direction = 1
            else:
                x_step_direction = -1
            center_y = midline_curve.y_vec[index]
            furthest_y = center_y
            center_x = midline_curve.x_vec[index]
            dx=0
            while True:
                new_dx = dx + x_step_direction
                new_y = furthest_y + dx*inv_slope
                if not full_curve.has_point_close_to(center_x + new_dx, new_y, error = .1):
                    break
                dx = new_dx
                furthest_y = new_y
            dy = furthest_y - center_y
            print(furthest_y, full_curve.get_y_at(new_dx + center_x))
            amplitude = pow(pow(dx, 2) + pow(dy, 2), 1/2)
            amplitudes.append(amplitude)
            x_vals.append(center_x)
    amplitude_curve = Curve(x_vals, amplitudes)
    return amplitude_curve


def find_relative_max(list):
    block_starting_index = 0
    prev_val = -1000
    current_val = list[block_starting_index]
    indices = []
    for index in range(len(list)):
        val = list[index]
        if prev_val < current_val and val < current_val:
            avg_index = int((index - 1 + block_starting_index) / 2)
            indices.append(avg_index)
        if current_val is not val:
            cur = current_val
            current_val = val
            prev_val = cur
            block_starting_index = index
    return indices

def find_relative_min(list):
    block_starting_index = 0
    prev_val = 1000
    current_val = list[block_starting_index]
    indices = []
    for index in range(len(list)):
        val = list[index]
        if prev_val > current_val and val > current_val:
            avg_index = int((index - 1 + block_starting_index) / 2)
            indices.append(avg_index)
        if current_val is not val:
            cur = current_val
            current_val = val
            prev_val = cur
            block_starting_index = index
    return indices

def find_starting_index(root_crop, image_folder_path):
    index_offset = IMGS_IN_24_HRS
    image_names = os.listdir(image_folder_path)
    natsort.natsorted(image_names, reverse=False)
    for index in range(len(image_names)):
        name = image_names[index]
        path = tools.make_path(image_folder_path, name)
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        image = cropper.crop(image, x_top_crop=root_crop.x_top_crop, y_top_crop=root_crop.y_top_crop,
                             x_bottom_crop=root_crop.x_base_crop, y_bottom_crop=root_crop.y_base_crop).image
        retval, threshed = cv2.threshold(image, ROOT_THRESHOLD, MAX, type=cv2.THRESH_BINARY)
        cropped = cropper.crop(threshed, y_bottom_crop=int(.9 * threshed.shape[0])).image
        if cropped is not tools.is_blank(cropped):
            index+=index_offset
            #tools.show_image(image)
            print(index)
            return index
    return index_offset

def get_timed_root_data(water, roots, image_folder_path, max_proj_filename):
    crops = []
    for root in roots:
        x_top_crop = root.x_top_crop + water.x_top_crop + X_TOP_CROP
        x_base_crop = root.x_base_crop + water.x_base_crop + X_BOTTOM_CROP
        y_top_crop = root.y_top_crop + water.y_top_crop + Y_TOP_CROP
        y_base_crop = root.y_base_crop + water.y_base_crop + Y_BOTTOM_CROP
        crop = CropStruct(x_base_crop=x_base_crop, x_top_crop=x_top_crop, y_top_crop=y_top_crop,
                          y_base_crop=y_base_crop)
        crops.append(crop)

    roots = []
    for index in range(len(crops)):
        root_crop = crops[index]
        start_index = find_starting_index(root_crop, image_folder_path)
        water, all_roots = find_interest_regions(image_folder_path, max_proj_filename, start_index)
        relevant_root = all_roots[index]
        roots.append(relevant_root)


def remove_extra_roots(root):
    contours, hier = cv2.findContours(root, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    max_area = 0
    max_index = 0
    for index in range(len(contours)):
        contour = contours[index]
        #cv2.drawContours(root, [contour], 0, 0, -1)
        x, y, w, h=cv2.boundingRect(contour)
        area = w*h
        if area > max_area:
            max_area = area
            max_index = index
            y_bottom_crop = root.shape[0] - (y + h + SAFETY_OFFSET_ROOTS)
    y_top_crop = 0
    #tools.show_image(root)
    for index in range(len(contours)):
        length = h + y
        if index is not max_index and length > y_top_crop:
            y_top_crop = length
    y_top_crop+=SAFETY_OFFSET_ROOTS
    return cropper.crop(root, y_top_crop=y_top_crop, y_bottom_crop=y_bottom_crop).image


def graph_curves(all_curves):
    curve_num = len(all_curves)
    fig, axes = plt.subplots(curve_num, 2)
    row = 0
    for key in all_curves.keys():
        curve_pair = all_curves[key]
        axes[row, 0].plot(curve_pair.full_curve.x_vec, curve_pair.full_curve.y_vec)
        #axes[row, 0].title.set_text("Horizontal Displacement vs. Time for Root " + str(key))
        #axes[row, 0].set_ylabel("Horizontal Displacement (mm)")
        #axes[row, 0].set_xlabel("Time Since Root Emergence (Hours)")
        axes[row, 1].plot(curve_pair.amplitude_curve.x_vec, curve_pair.amplitude_curve.y_vec)
        #axes[row, 1].title.set_text("Root Tip Rotational Amplitude vs. Time for Root " + str(key))
        #axes[row, 1].set_ylabel("Rotational Amplitude (mm)")
        #axes[row, 1].set_xlabel("Time Since Root Emergence (Hours)")
        row+=1
    plt.show()

def graph(curve):
        plt.plot(curve.x_vec, curve.y_vec)
        plt.figure()