#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse HPCG output txt files -> kernel timings, GFLOP/s, bandwidth, Allreduce."""
import json
import re
import glob

BASE = "/home/longm/asc-hpcg/results"
files = {
    "g1_pure_mpi": sorted(glob.glob(f"{BASE}/g1_pure_mpi*.txt")),
    "g2_hybrid": sorted(glob.glob(f"{BASE}/g2_hybrid_43*.txt")),
    "g3_pure_omp": sorted(glob.glob(f"{BASE}/g3_pure_omp*.txt")),
}


def grab(text, pattern, cast=float):
    m = re.search(pattern, text)
    return cast(m.group(1)) if m else None


out = {}
for tag, fl in files.items():
    if not fl:
        continue
    t = open(fl[0], encoding="utf-8", errors="replace").read()
    out[tag] = {
        "time_ddot": grab(t, r"Benchmark Time Summary::DDOT=([\d.e+-]+)"),
        "time_waxpby": grab(t, r"Benchmark Time Summary::WAXPBY=([\d.e+-]+)"),
        "time_spmv": grab(t, r"Benchmark Time Summary::SpMV=([\d.e+-]+)"),
        "time_mg": grab(t, r"Benchmark Time Summary::MG=([\d.e+-]+)"),
        "time_total": grab(t, r"Benchmark Time Summary::Total=([\d.e+-]+)"),
        "gf_ddot": grab(t, r"GFLOP/s Summary::Raw DDOT=([\d.e+-]+)"),
        "gf_waxpby": grab(t, r"GFLOP/s Summary::Raw WAXPBY=([\d.e+-]+)"),
        "gf_spmv": grab(t, r"GFLOP/s Summary::Raw SpMV=([\d.e+-]+)"),
        "gf_mg": grab(t, r"GFLOP/s Summary::Raw MG=([\d.e+-]+)"),
        "gf_total": grab(t, r"GFLOP/s Summary::Raw Total=([\d.e+-]+)"),
        "bw_total": grab(t, r"GB/s Summary::Raw Total B/W=([\d.e+-]+)"),
        "bw_read": grab(t, r"GB/s Summary::Raw Read B/W=([\d.e+-]+)"),
        "mem_gb": grab(t, r"Total memory used for data \(Gbytes\)=([\d.e+-]+)"),
        "allreduce_avg": grab(t, r"DDOT Timing Variations::Avg DDOT MPI_Allreduce time=([\d.e+-]+)"),
        "allreduce_min": grab(t, r"DDOT Timing Variations::Min DDOT MPI_Allreduce time=([\d.e+-]+)"),
        "allreduce_max": grab(t, r"DDOT Timing Variations::Max DDOT MPI_Allreduce time=([\d.e+-]+)"),
        "bytes_per_eq": grab(t, r"Bytes per equation \(Total memory / Number of Equations\)=([\d.e+-]+)"),
    }

print(json.dumps(out, indent=1))
with open("/home/longm/asc-hpcg/results/kernel_summary.json", "w") as f:
    json.dump(out, f, indent=1)
print("saved kernel_summary.json")
