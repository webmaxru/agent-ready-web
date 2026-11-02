# figures/src

One SVG per figure, named after the figure number: `figure-N-M.svg` for Figure N.M (`figure-A-1.svg` in an appendix). Follow [`../PALETTE.md`](../PALETTE.md) and the classes in [`../figure.css`](../figure.css). `python3 figures/render.py figure-N-M` renders it to `manuscript/resources/images/figure-N-M.png`, which the chapter references as `images/figure-N-M.png`. Empty until the chapters add their figures.
