---
# Documentation: https://wowchemy.com/docs/managing-content/

title: 'RESPACK: An ab initio tool for derivation of effective low-energy model of
  material'
subtitle: ''
summary: ''
authors:
- Kazuma Nakamura
- Yoshihide Yoshimoto
- Yusuke Nomura
- admin
- Mitsuaki Kawamura
- Taichi Kosugi
- Kazuyoshi Yoshimi
- Takahiro Misawa
- Yuichi Motoyama
tags:
- Effective model derivation from first principles; Many-body perturbation calculation;
  Maximally localized Wannier function
categories: []
date: '2021-04-01'
lastmod: 2023-06-01T20:39:38+09:00
featured: false
draft: false

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder.
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: ''
  focal_point: ''
  preview_only: false

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects: []
publishDate: '2023-06-01T11:39:38.488124Z'
publication_types:
- '2'
abstract: "RESPACK is a first-principles calculation software for evaluating the interaction\
  \ parameters of materials and is able to calculate maximally localized Wannier functions,\
  \ response functions based on the random phase approximation and related optical\
  \ properties, and frequency-dependent electronic interaction parameters. RESPACK\
  \ receives its input data from a band-calculation code using norm-conserving pseudopotentials\
  \ with plane-wave basis sets. Automatic generation scripts that convert the band-structure\
  \ results to the RESPACK inputs are prepared for xTAPP and Quantum ESPRESSO. An\
  \ input file for specifying the RESPACK calculation conditions is designed pursuing\
  \ simplicity and is given in the Fortran namelist format. RESPACK supports hybrid\
  \ parallelization using OpenMP and MPI and can treat large systems including a few\
  \ hundred atoms in the calculation cell. Program summary Program Title: RESPACK\
  \ CPC Library link to program files: https://dx.doi.org/10.17632/3cxb7474nj.1 Developer's\
  \ repository link: https://sites.google.com/view/kazuma7k6r Licensing provisions:\
  \ GNU General Public Licence v3.0 Programming language: Fortran, Python External\
  \ routines: LAPACK, BLAS, MPI Nature of problem: Ab initio calculations for maximally\
  \ localized Wannier function, response function with random-phase approximation,\
  \ and matrix-element evaluations of frequency-dependent screened direct and exchange\
  \ interactions. With this code, an effective low-energy model of materials is derived\
  \ from first principles. Solution method: Our method is based on ab initio many-body\
  \ perturbation calculation and the maximally localized Wannier function calculation.\
  \ The program employs the plane-wave basis set, and evaluations of matrix elements\
  \ are performed with the fast Fourier transformation. The generalized tetrahedron\
  \ method is used for the Brillouin Zone integral. Additional comments including\
  \ restrictions and unusual features: RESPACK supports xTAPP and Quantum ESPRESSO\
  \ packages, and automatic generation scripts for converting the band-calculation\
  \ results to the RESPACK inputs are prepared for these software. The current RESPACK\
  \ only supports band-calculation codes using norm-conserving pseudopotentials with\
  \ plane-wave basis sets. RESPACK supports hybrid parallelization using OpenMP and\
  \ MPI to treat large systems in which a few hundred atoms are contained in unit\
  \ cell."
publication: '*Comput. Phys. Commun.*'
---
