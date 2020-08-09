from compiler import Config
from compiler import Transformer
import gast as ast
import astor
import sys, os
sys.path.append(os.path.dirname(sys.path[0]))

class Compiler():
  def compile(self, f):
    cfg = Config("playground/compile.config.json")
    cfg.dumpConfig()
    tree = ast.parse(f.read())
    print(">>>>>>>>>>>> Before")
    print(astor.dump_tree(tree))
    print(">>>>>>>>>>>> Analyzing & Transforming ...")
    transformer = Transformer(tree, cfg)
    new_tree = transformer.visit(tree)
#    print(">>>>>>>>>>>> Complete")
#    print(astor.dump_tree(new_tree))
    return astor.to_source(ast.gast_to_ast(new_tree))
