
pacman:
	@mkdir -p _build/pacman
	@cd _build/pacman/; 				\
	cp ../../PKGBUILD ./;               \
	makepkg --skipinteg --syncdeps -f

clean:
	rm -rf _build/
