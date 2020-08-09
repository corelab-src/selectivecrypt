import json
from compiler import Config
import gast as ast
import beniget, astor

class Analyzer(ast.NodeVisitor):
  def __init__(self, module_node, cfg):
    self.chains = beniget.DefUseChains()
    self.chains.visit(module_node) # make use-def chains
    self.users = set()  # users of local definitions
    # filtered_defs: defs who has no use but 'noproc_uses' from config.
    # so these defs can be encrypted with AES.
    self.filtered_defs = set() 
    self.target_def_use = {} # transform target defs and corresponding uses. 
    self.cfg = cfg # configuration
    self.he_aes = {} 
    self.analysis_file = open("data/analysis.json", "w")

  def visit_FunctionDef(self, node):
    if node.name in self.cfg.target_funcs:
      for def_ in self.chains.locals[node]:
        # initialize the set of node using a local variable
        self.users.update(use.node for use in def_.users())
        for user in def_.users():
          for use in user.users():
            if len(def_.users()) == 1:
              if isinstance(use.node, ast.Call) and \
                 isinstance(use.node.func, ast.Attribute):
                for exception in self.cfg.exceptional_uses:
                  if use.node.func.attr == exception:
                    self.filtered_defs.add(def_.name())

    self.generic_visit(node)
    return node

  def visit_Assign(self, node):
    for data_in_func in self.cfg.data_in:
      if node.targets[0].id not in self.filtered_defs and \
         isinstance(node.value, ast.Call) and \
         ((isinstance(node.value.func, ast.Name) and \
          node.value.func.id == data_in_func) or \
          (isinstance(node.value.func, ast.Attribute) and \
           node.value.func.attr == data_in_func)):
        for node_ in self.users:
          if node_.id == node.targets[0].id:
            ud = self.chains.chains[node_]
            for user in ud.users():
              self.target_def_use[node.targets[0].id] = user
    self.generic_visit(node)
    return node

  def emitAnalysisResult(self):
    # Emit analysis results
    self.he_aes = {
      'HE': [d for d, u in self.target_def_use.items()], 
      'AES': list(self.filtered_defs)
    }
    json.dump(self.he_aes, self.analysis_file, indent=2)
    self.analysis_file.close()
    
