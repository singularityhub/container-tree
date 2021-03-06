# Container Tree 

SLURM Version! Here we will generate the [container tree](https://www.github.com/singularityhub/container-tree) in parallel on a SLURM
cluster, since it takes a long time to do in serial! I'll show how to run it natively, and I want to add some 
perspective on how I found this experience. It was annoying and hard. I have since forgotten how hard it is to run
things on a shared cluster, because I'm so used to creating a container, and just using it. I'll share the experience
anyway, but thank god for containers. And honestly, I hope that we and research computing can up our game with
respect to the number of steps I need to take to run a simple script. This just isn't good enough.

## Get an Interactive Node
For generating the database, a one time thing that I don't need to create a batch script for, I'll use an
interactive node. `sdev` didn't work because the default ran out of memory.
You can't ask for enough using `sdev`, so I wound up using `srun`. Why was this frustrating? Because
it took easily 5 minutes to actually get a node. I feel for my previous life grad student, and all
the current graduate students.

```python
srun --mem 32000 --pty bash
```

Finally we continue! Let's load python.

## Load Dependencies

### Python
Yes, we will need Python, and Python 3 at that.

```bash
module load python/3.6.1
```
I again got tripped up here. Why? I expected my default `python`  to be loaded now as python 3. Was it?

```bash
python --version
Python 2.7.5
```

Nope. Apparently this is set up to load only as Python 3, which I only figured out with
trial and error. I'm *supposed* to be reading some docs somewhere, but as a typical user trust me,
I'm not. Let's continue and install container tree, now that we've found our Python. I'm going to be
conservative and call the pip module *from* python so I know it's the right one.

```bash
python3 -m pip install --user containertree
```

### Scripts and Working Location
Then we can create a nice working space in our scratch by cloning the repo to get these files.

```bash
cd $SCRATCH/WORK 
git clone https://www.github.com/singularityhub/container-tree
cd container-tree/examples/summary_tree_slurm
```

## Generate Database
Now we can generate a database pickle!

```bash
python3 generate.py database.pkl
Selecting container from https://singularityhub.github.io/api/files...
Generating comparison tree!
Adding 54r4/sara-server-vre
Adding A33a/sjupyter
Adding A33a/sjupyter@f15489984e4d7751b9e6869553084e5b
...
Adding YeoLab/rnashapes@29dfd29177d87eb3dde613580f65f6a6
Adding YeoLab/rnashapes@19373b5a2b5d8a6b98819ef62d062299
Adding YeoLab/rnashapes@2d37f3d76367369e8495bdfd7e1c9561
Saving to database.pkl
```

## Submit Jobs
Once we have our database.pkl, we can submit SLURM jobs to do comparisons!
This looks trivial here, but in reality it took me a good 30-40 minutes to write
these scripts, run out of memory several times, wait around for nodes, and then
want to strangle someone. I suspect this is the typical user experience.

The basic idea is that the script [run.py](run.py) will be used to generate a
vector of scores for one container (compared to all others) and
[run_all.py](run_all.py) will generate a `run_jobs.sh` script to submit instances of it
to sbatch. When the jobs finish, the script [combine.py](combine.py) 
will compile the result into one nice object :) Yes, this is annoying as heck
to just run a sequence of commands.

### Generate Job Submission Script
To generate `run_jobs.sh` we need to load the database, and create a jobs and result
folder in our present working directory, and write an sbatch job file for each job (container) 
we want to run.

```bash
python run_all.py
```
This generated the jobs:

```bash
ls jobs/
containertree0.err    containertree3.out  run_101.sh  run_115.sh  run_129.sh  run_142.sh  run_156.sh  run_16.sh   run_183.sh  run_22.sh  run_36.sh  run_4.sh   run_63.sh  run_77.sh  run_90.sh
containertree0.out    containertree4.err  run_102.sh  run_116.sh  run_12.sh   run_143.sh  run_157.sh  run_170.sh  run_184.sh  run_23.sh  run_37.sh  run_50.sh  run_64.sh  run_78.sh  run_91.sh
containertree10.err   containertree4.out  run_103.sh  run_117.sh  run_130.sh  run_144.sh  run_158.sh  run_171.sh  run_185.sh  run_24.sh  run_38.sh  run_51.sh  run_65.sh  run_79.sh  run_92.sh
...
```

### Test the Job
You'll notice in the above listing I had already started testing, because I have output and error files. First, let's test one job. I opened up
the run_jobs.sh script to get one last line, and run it manually:

```bash
sbatch -p russpold /scratch/users/vsochat/WORK/container-tree/examples/summary_tree_slurm/jobs/run_192.sh
```

You can look at the output and error files to see how you screwed up. Trust me, you will.

```bash
cat jobs/containertree192.err
```

What errors did I have? I forgot to load a module first. Then I added the line and forget to end the `writelines`
command with a newline. Then I loaded the wrong version of python and it didn't find the module.
 I wouldn't have known these issues without looking at the error files. I also needed to check 
continuously on if the job was running, period, with:

```bash
squeue --user vsochat
```

Then check that your output is generated successfully. Is the correct data there?

```bash
ls result/
```

### Submit All Jobs
When you are content that you are done screwing up, submit all jobs:

```bash
bash run_all.sh
```

Then pray.


## Compile Result

Once the jobs have finished running, your output folder should be robust with pickles!

```bash
ls result/

```

And you can use combine.py to combine them. Note that it's going to generate
a data.json in the present working directory. If you did this more nicely, you would
have written a script to take this as an input argument.

```bash
python3 combine.py
```

I'm too ornery with cluster computing to do this nicely :)
