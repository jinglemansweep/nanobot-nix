# Docker Build Failure

1.963 Note: a multi-user installation is possible. See https://nix.dev/manual/nix/stable/installation/installing-binary.html#multi-user-installation
1.965 performing a single-user installation of Nix...
1.965 warning: installing Nix as root is not supported by this script!
1.965 directory /nix does not exist; creating it by running 'mkdir -m 0755 /nix && chown root /nix' using sudo
1.965 /tmp/nix-binary-tarball-unpack.9P7vJmVIDj/unpack/nix-2.33.3-x86_64-linux/install: 149: sudo: not found
1.965 /tmp/nix-binary-tarball-unpack.9P7vJmVIDj/unpack/nix-2.33.3-x86_64-linux/install: please manually run 'mkdir -m 0755 /nix && chown root /nix' as root to create /nix
------
[+] build 0/1
 ⠙ Image ghcr.io/jinglemansweep/nanobot-nix:latest Building                                                                                                                               38.4s
Dockerfile:52
--------------------
  51 |     ENV USER=root
  52 | >>> RUN curl -sL https://nixos.org/nix/install | sh -s -- --no-daemon && \
