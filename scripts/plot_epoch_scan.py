#!/usr/bin/env python3
"""Plot results/epoch_scan/target_residuals_by_year.csv (requires matplotlib)."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

STYLE = {'Kings_adopted': ('-', '45.00° (adopted)'), 'Kings_Petrie': ('--', '45.22° (Petrie)'),
         'Queens_adopted': ('-', '39.6078° (adopted)'), 'Queens_40': ('--', '40.00° (alternative)')}
COLOUR = {'Mintaka': '#1b9e77', 'Alnilam': '#d95f02', 'Alnitak': '#7570b3', 'Sirius': '#e7298a'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', default='results/epoch_scan/target_residuals_by_year.csv')
    p.add_argument('--output', default='results/epoch_scan/epoch_scan.png')
    p.add_argument('--reference-year', type=int, default=-2549)
    a = p.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    series = defaultdict(lambda: ([], []))
    for r in csv.DictReader(Path(a.input).open(newline='')):
        x, y = series[r['chamber'], r['case_id'], r['name']]
        x.append(1 - int(r['year_astronomical']))
        y.append(float(r['residual_deg']))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, chamber, title in zip(axes, ('Kings', 'Queens'), ("King's Chamber southern shaft", "Queen's Chamber southern shaft")):
        ax.axhspan(-0.2, 0.2, color='0.9', zorder=0, label='±0.2° reference band')
        ax.axhline(0, color='0.4', lw=0.8)
        ax.axvline(1 - a.reference_year, color='0.4', lw=0.8, ls=':', label=f'{1 - a.reference_year} BCE (paper)')
        for (ch, case, name), (x, y) in sorted(series.items(), key=lambda kv: (list(STYLE).index(kv[0][1]), kv[0][2])):
            if ch == chamber:
                ls, lab = STYLE[case]
                ax.plot(x, y, ls, color=COLOUR[name], lw=1.6, label=f'{name}, {lab}')
        ax.set_title(title)
        ax.set_xlabel('Year (BCE)')
        ax.invert_xaxis()
        ax.set_ylim(-2, 2)
        ax.grid(alpha=0.3)
        ax.legend(fontsize=8, loc='upper left')
    axes[0].set_ylabel('Meridian altitude − shaft inclination (°)')
    fig.tight_layout()
    fig.savefig(a.output, dpi=200)
    print(f'Wrote {a.output}')


if __name__ == '__main__':
    main()
