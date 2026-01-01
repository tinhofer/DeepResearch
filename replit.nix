{pkgs} : {
  deps = [
    pkgs.alsa-lib
    pkgs.libdrm
    pkgs.freetype
    pkgs.fontconfig
    pkgs.expat
    pkgs.cups
    pkgs.dbus
    pkgs.atk
    pkgs.nss
    pkgs.nspr
    pkgs.glib
    pkgs.gtk3
    pkgs.gdk-pixbuf
    pkgs.cairo
    pkgs.pango
    pkgs.libglvnd
    pkgs.libGL
    pkgs.xorg.libxcb
    pkgs.xorg.libXxf86vm
    pkgs.xorg.libXft
    pkgs.xorg.libXinerama
    pkgs.xorg.libXrandr
    pkgs.xorg.libXtst
    pkgs.xorg.libXrender
    pkgs.xorg.libXi
    pkgs.xorg.libXfixes
    pkgs.xorg.libXext
    pkgs.xorg.libXdamage
    pkgs.xorg.libXcursor
    pkgs.xorg.libXcomposite
    pkgs.xorg.libX11
    pkgs.ffmpeg-full
    pkgs.playwright-driver
    pkgs.gitFull
  ];
  env = {
    PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
    PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
  };
}
