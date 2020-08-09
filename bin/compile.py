import sys, os, time
sys.path.append(os.path.dirname(sys.path[0]))
from compiler import Compiler

def main(argv):
  if len(argv) != 3:
    print("Usage:")
    print("python compile.py [input] [output_path]")
    sys.exit()
  inputfile = argv[1]
  output_path = argv[2]
  c = Compiler()
  with open(inputfile,'r') as f:
    start = time.time()
    out = c.compile(f)
    diff = time.time() - start
    print(">>>>>>>>>> Compilation in {}ms)".format(diff*1000))
#    print(out)
    sliced = os.path.basename(inputfile.split('.')[0])
    with open(output_path + "/{}_transformed.py".format(sliced), "w") as fo:
      fo.write(out)
      fo.close()

if __name__ == "__main__":
  main(sys.argv)
