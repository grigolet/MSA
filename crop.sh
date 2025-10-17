mkdir -p cropped
for f in photo_*.jpg; do
  magick "$f" -crop 417x380+447+170 +repage "cropped/$f"
done
magick cropped/*.jpg -append stitched.png