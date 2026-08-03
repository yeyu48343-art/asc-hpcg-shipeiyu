# ASC 选拔作业 - 基础题 HPCG

## 基本信息

- **姓名**：石培玉
- **学号**：240809010102
- **年级专业**：计算机科学与技术 24 级
- **题目**：HPCG（High Performance Conjugate Gradient）基准测试
- **题目链接**：https://github.com/hpcg-benchmark/hpcg

## 机器环境

| 项目 | 配置 |
|------|------|
| 操作系统 | Windows 11 + WSL2 Ubuntu 24.04 |
| 内核 | Linux 6.6.87.2-microsoft-standard-WSL2 |
| CPU | Intel Core i5-12500H (4 P-core + 8 E-core, 16 逻辑核) |
| 内存 | 16 GB DDR5 |
| 编译器 | g++ 13.3.0 (Ubuntu 24.04) |
| MPI | Open MPI 5.0.8 |
| OpenMP | 4.5 (libgomp) |
| CMake | 4.3.0 |

## 编译步骤

```bash
git clone https://github.com/hpcg-benchmark/hpcg.git
cd hpcg
mkdir build && cd build
cmake .. -DHPCG_ENABLE_MPI=ON -DHPCG_ENABLE_OPENMP=ON \
         -DCMAKE_CXX_COMPILER=mpicxx \
         -DCMAKE_POLICY_VERSION_MINIMUM=3.5
make -j12
# 产物：build/xhpcg
```

> 注：CMake 4.x 移除了对 < 3.5 的兼容，需加 `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`。

## 运行配置

三组对比配置，**统一全局规模 96×96×96**（公平对比），每组运行 60 秒：

| 组 | MPI 进程 | OpenMP 线程 | 每进程网格 | 进程网格 P×Q×R | 运行命令 |
|----|----------|-------------|------------|----------------|----------|
| 组1 纯 MPI | 12 | 1 | 32×48×48 | 3×2×2 | `OMP_NUM_THREADS=1 mpirun -np 12 --oversubscribe ./xhpcg` |
| 组2 混合 | 4 | 3 | 48×48×96 | 2×2×1 | `OMP_NUM_THREADS=3 mpirun -np 4 --oversubscribe ./xhpcg` |
| 组3 纯 OpenMP | 1 | 12 | 96×96×96 | 1×1×1 | `OMP_NUM_THREADS=12 ./xhpcg` |

> `hpcg.dat` 必须用**小写文件名**，放在 `xhpcg` 同目录，5 行格式：注释×2 + `nx ny nz` + `runtime` + `Px Py Pz`。
> 每个维度的网格数必须能被 2 整除（HPCG 多重网格粗化要求）。

## 实验结果

| 组 | 配置 | GFLOP/s | 运行时间(s) | VALID |
|----|------|---------|-------------|-------|
| 组1 纯 MPI (12×1) | 12 进程 × 1 线程 | **3.62** | 66.25 | ✅ VALID |
| 组2 混合 (4×3) | 4 进程 × 3 线程 | **2.25** | 64.20 | ✅ VALID |
| 组3 纯 OpenMP (1×12) | 1 进程 × 12 线程 | **1.08** | 74.17 | ✅ VALID |

**最优配置：组1 纯 MPI（12 进程 × 1 线程），GFLOP/s = 3.62**

### 结果分析

1. **纯 MPI 最快**：12 个独立进程，每个有独立地址空间，避免 OpenMP 共享内存的 false sharing 和 cache 冲突。HPCG 是内存带宽密集型基准，多进程的内存隔离反而有利。

2. **混合模式次之**：4 进程 × 3 线程，进程内 OpenMP 共享内存有少量竞争，但进程数少减少了 MPI 通信开销。

3. **纯 OpenMP 最慢**：12 线程共享单一地址空间，对 HPCG 的稀疏矩阵向量乘（SpMV）和多网格（MG）操作，多线程争抢同一块内存带宽，且 i5-12500H 异构 P/E 核导致负载不均。

## 复现方式

```bash
# 1. 编译（见上文）
# 2. 进入 build 目录
cd hpcg/build
# 3. 选择一组配置，复制对应的 hpcg.dat
cp /path/to/configs/g1_pure_mpi.dat hpcg.dat   # 或 g2/g3
# 4. 运行（对应命令见上表）
OMP_NUM_THREADS=1 mpirun -np 12 --oversubscribe ./xhpcg
# 5. 查看结果
grep "HPCG result is" HPCG-Benchmark_*.txt
```

## 文件说明

```
asc-hpcg/
├── README.md                      ← 本文件
├── configs/                       ← 三组 hpcg.dat 配置
│   ├── g1_pure_mpi.dat
│   ├── g2_hybrid_43.dat
│   └── g3_pure_omp.dat
└── results/                       ← 三组完整结果 + 汇总
    ├── g1_pure_mpi.txt            ← 组1 完整 HPCG 输出
    ├── g2_hybrid_43.txt           ← 组2 完整 HPCG 输出
    ├── g3_pure_omp.txt            ← 组3 完整 HPCG 输出
    └── summary.csv                ← 三组关键数据汇总
```

## 注意事项

- HPCG 正式提交要求运行时间 ≥ 1800 秒（30 分钟）。本次为作业对比实验，运行 60 秒即可得到合法 VALID 结果和 GFLOP/s 评分。
- WSL2 跑在 Hyper-V 虚拟机里，缺少 NUMA 拓扑感知，绝对性能低于裸机；但三组配置在同一环境下的**相对对比**是公平可信的。
- i5-12500H 是 4 P-core + 8 E-core 异构架构，E-core 单核性能约为 P-core 的 60-70%，这会影响多线程负载均衡。
