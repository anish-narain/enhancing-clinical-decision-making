non_fine_tuned = ['mort-ind-nft.png', 'mort-seq-nft.png', 'mort-joint-nft.png']
early_stopping = ['mort-ind-es.png', 'mort-seq-es.png', 'mort-joint-es.png']
l2_regularised = ['mort-ind-l2.png', 'mort-seq-l2.png', 'mort-joint-l2.png']

# Define the file path prefix
file_path_prefix = 'imgs/'

# Define image sets and output filenames with updated paths
image_sets = [
    ([file_path_prefix + 'mort-ind-nft.png', file_path_prefix + 'mort-seq-nft.png', file_path_prefix + 'mort-joint-nft.png'], "combined_non_fine_tuned.png"),
    ([file_path_prefix + 'mort-ind-es.png', file_path_prefix + 'mort-seq-es.png', file_path_prefix + 'mort-joint-es.png'], "combined_early_stopping.png"),
    ([file_path_prefix + 'mort-ind-l2.png', file_path_prefix + 'mort-seq-l2.png', file_path_prefix + 'mort-joint-l2.png'], "combined_l2_regularised.png")
]

# Create and save combined images for each set
for images, output_filename in image_sets:
    create_combined_image_row(images, output_filename)