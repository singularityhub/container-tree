# Container Tree 

SLURM Version! Here we will generate the [container tree](https://www.github.com/singularityhub/container-tree) in parallel on a SLURM
cluster, since it takes a long time to do in serial! I'll note that I first tried
running this locally on Sherlock, got a weird error with pip almost immediately,
and went right back to building a container. Thank goodness for containers! 
First, let's pull out container.

```bash
module load singularity/2.5
export SINGULARITY_CACHEDIR=$SCRATCH/.singularity
singularity pull docker://vanessa/container-tree
```

Then we can create a nice working space in our scratch by cloning the repo to get these files.

```bash
cd $SCRATCH/WORK 
mkdir container-tree && cd container-tree
```

Grab an interactive node before we break something...

```python
sdev
```
