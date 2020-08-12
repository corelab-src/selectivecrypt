from compiler import Config
from compiler import Analyzer
import gast as ast
import beniget, astor
    
class Transformer(ast.NodeTransformer):
  def __init__(self, module_node, cfg):
    self.chains = beniget.DefUseChains()
    self.chains.visit(module_node)
    self.ancestors = beniget.Ancestors()
    self.ancestors.visit(module_node)
    self.analysis = Analyzer(module_node, cfg)
    self.analysis.visit(module_node)
    self.analysis.emitAnalysisResult()
    self.cfg = cfg
  
  def visit_Module(self, node):
    import_mypyheal = ast.ImportFrom(
        module="utils.mypyheal",
        names=[ast.alias("MyPyHeal", "ph")],
        level=0)
    import_wrapper = ast.ImportFrom(
        module="pyheal",
        names=[ast.alias("wrapper", None)],
        level=0)
    import_ciphertext_op = ast.ImportFrom(
        module="pyheal",
        names=[ast.alias("ciphertext_op", None)],
        level=0)
    node.body.insert(0, import_ciphertext_op)
    node.body.insert(0, import_wrapper)
    node.body.insert(0, import_mypyheal)
    ast.NodeVisitor.generic_visit(self, node)
    return node
  
  def visit_FunctionDef(self, node):
    if node.name in self.cfg.target_funcs:
      download_parms = ast.Expr(
        ast.Call(
          func=ast.Attribute(
            value=ast.Name('s3', ast.Load(), None, None),
              attr='download_file',
              ctx=ast.Load()),
            args=[
              ast.Constant('selcrypt', None),
              ast.Constant('seal.parms', None),
              ast.Constant('/tmp/seal.parms', None)
            ],
            keywords=[])
      )
      download_pubkey = ast.Expr(
        ast.Call(
          func=ast.Attribute(
            value=ast.Name('s3', ast.Load(), None, None),
              attr='download_file',
              ctx=ast.Load()),
            args=[
              ast.Constant('selcrypt', None),
              ast.Constant('pub.key', None),
              ast.Constant('/tmp/pub.key', None)
            ],
            keywords=[])
      )
      download_relinkey = ast.Expr(
        ast.Call(
          func=ast.Attribute(
            value=ast.Name('s3', ast.Load(), None, None),
              attr='download_file',
              ctx=ast.Load()),
            args=[
              ast.Constant('selcrypt', None),
              ast.Constant('relin.key', None),
              ast.Constant('/tmp/relin.key', None)
            ],
            keywords=[])
      )

      open_parms_in = ast.withitem(
        context_expr=ast.Call(
          func=ast.Name('open', ast.Load(), None, None),
          args=[ast.Constant('/tmp/seal.parms', None),
                ast.Constant('r', None)],
          keywords=[]),
        optional_vars=ast.Name('f', ast.Load(), None, None))
      read_parms_in = ast.Assign(
        targets=[ast.Name('parms_in', ast.Store(), None, None)],
        value=ast.Call(
          func=ast.Attribute(
            value=ast.Name('json', ast.Load(), None, None),
            attr='load',
            ctx=ast.Load()),
          args=[ast.Name('f', ast.Load(), None, None)],
          keywords=[]))
      make_heal_obj = ast.Assign(
        targets=[ast.Name('heal', ast.Store(), None, None)],
        value=ast.Call(
          func=ast.Name('ph', ast.Load(), None, None),
          args=[],
          keywords=[
            ast.keyword(
              arg='poly_modulus',
              value=ast.Subscript(
                value=ast.Name('parms_in', ast.Load(), None, None),
                slice=ast.Constant('poly_modulus', None),
                ctx=ast.Load()
              )
            ),
            ast.keyword(
              arg='coeff_modulus',
              value=ast.Subscript(
                value=ast.Name('parms_in', ast.Load(), None, None),
                slice=ast.Constant('coeff_modulus', None),
                ctx=ast.Load()
              )
            ),
            ast.keyword(
              arg='plain_modulus',
              value=ast.Subscript(
                value=ast.Name('parms_in', ast.Load(), None, None),
                slice=ast.Constant('plain_modulus', None),
                ctx=ast.Load()
              )
            ),
            ast.keyword(
              arg='pubkey_path',
              value=ast.Constant('/tmp/pub.key', None)
            )
            #ast.keyword(
            #  arg='seckey_path',
            #  value=ast.Constant('data/sec.key', None)
            #)
          ] # keywords
        ) # call
      ) # assign
      
      with_recover_ctx = ast.With(
        items=[open_parms_in],
        body=[read_parms_in,
              make_heal_obj],
        type_comment=None) 
      
      recover_plaintext_encoder = ast.Assign(
        targets=[ast.Name('plaintext_encoder', ast.Store(), None, None)],
        value=ast.Attribute(
          value=ast.Name('heal', ast.Load(), None, None),
          attr='plaintext_encoder',
          ctx=ast.Load())
      )  
      recover_encryptor_encoder = ast.Assign(
        targets=[ast.Name('encryptor_encoder', ast.Store(), None, None)],
        value=ast.Attribute(
          value=ast.Name('heal', ast.Load(), None, None),
          attr='encryptor_encoder',
          ctx=ast.Load())
      )  
      #recover_decryptor_decoder = ast.Assign( # FIXME should be deleted
      #  targets=[ast.Name('decryptor_decoder', ast.Store(), None, None)],
      #  value=ast.Attribute(
      #    value=ast.Name('heal', ast.Load(), None, None),
      #    attr='decryptor_decoder',
      #    ctx=ast.Load())
      #)  
      recover_evaluator = ast.Assign(
        targets=[ast.Name('evaluator', ast.Store(), None, None)],
        value=ast.Attribute(
          value=ast.Name('heal', ast.Load(), None, None),
          attr='evaluator',
          ctx=ast.Load())
      )  

      node.body.insert(0, recover_evaluator)
      #node.body.insert(0, recover_decryptor_decoder)
      node.body.insert(0, recover_encryptor_encoder)
      node.body.insert(0, recover_plaintext_encoder)
      node.body.insert(0, with_recover_ctx)
      node.body.insert(0, download_relinkey)
      node.body.insert(0, download_pubkey)
      node.body.insert(0, download_parms)
    self.generic_visit(node)
    return node
  """
  def visit_Name(self, node):
#    astor.dump_tree(node)
    if isinstance(node.ctx, ast.Load):
      node_in_chains = node in self.chains.chains
      if node_in_chains and node.id == 'p':
        for node_ in self.users:
          if node_.id == node.id:
            ud = self.chains.chains[node_]
            print(ud.name())
            for user in ud.users():
              print(astor.dump_tree(user.node))
            print('\n')
    self.generic_visit(node)
    return node
  """
  def visit_Assign(self, node):
    # find 'var = s3.download_[file|obj](...'
    for data_in_func in self.cfg.data_in:
      if node.targets[0].id not in self.analysis.filtered_defs and \
         isinstance(node.value, ast.Call) and \
         ((isinstance(node.value.func, ast.Name) and \
          node.value.func.id == data_in_func) or \
          (isinstance(node.value.func, ast.Attribute) and \
           node.value.func.attr == data_in_func)):
        """
        for node_ in self.users:
          if node_.id == node.targets[0].id:
            ud = self.chains.chains[node_]
            print(ud.name())
            for user in ud.users():
              print(astor.dump_tree(user.node))
        """ 
        generated = []
        for d, u in self.analysis.target_def_use.items():
  #        print(d)
  #        print(astor.dump_tree(u.node))
          if d == node.targets[0].id and \
             isinstance(u.node, ast.Call) and \
             isinstance(u.node.func, ast.Attribute):
            if u.node.func.value.id in self.cfg.plaintext_encode:
  #            print("in")
  #            print(self.cfg.plaintext_encode)
              download_ptxt = ast.Expr(
                ast.Call(
                  func=ast.Attribute(
                    value=ast.Name('s3', ast.Load(), None, None),
                    attr='download_file',
                    ctx=ast.Load()),
                  args=[
                    node.value.args[0],
                    node.value.args[1],
                    node.value.args[2]
                  ],
                  keywords=[])
              )
              init_ptxt = ast.copy_location(
                ast.Call(
                  func=ast.Attribute(
                    value=ast.Name('wrapper', ast.Load(), None, None),
                    attr='Plaintext',
                    ctx=ast.Load()),
                  args=[],
                  keywords=[]), node
              )
              assign = ast.copy_location(
                ast.Assign([node.targets[0]], init_ptxt), node
              )
              if self.cfg.mode == 'aws':
                generated.append(download_ptxt)
              generated.append(assign)
            else:
  #            print("not plain")
              download_ctxt = ast.Expr(
                ast.Call(
                  func=ast.Attribute(
                    value=ast.Name('s3', ast.Load(), None, None),
                    attr='download_file',
                    ctx=ast.Load()),
                  args=[
                    node.value.args[0],
                    node.value.args[1],
                    node.value.args[2]
                  ],
                  keywords=[])
              )
              init_ctxt = ast.copy_location(
                ast.Call(
                  func=ast.Attribute(
                    value=ast.Name('wrapper', ast.Load(), None, None),
                    attr='Ciphertext',
                    ctx=ast.Load()),
                  args=[],
                  keywords=[]), node
              )
              assign_init_ctxt = ast.copy_location(
                ast.Assign([node.targets[0]], init_ctxt), node
              )
              assign_ciphertext_op = ast.Assign(
                targets=[node.targets[0]],
                value=ast.Call(
                  func=ast.Attribute(
                    value=ast.Name('ciphertext_op', ast.Load(), None, None),
                    attr='CiphertextOp',
                    ctx=ast.Load()),
                  args=[],
                  keywords=[
                    ast.keyword(
                      arg='ciphertext',
                      value=node.targets[0]),
                    ast.keyword(
                      arg='evaluator',
                      value=ast.Name('evaluator', ast.Load(), None, None)),
                    ast.keyword(
                      arg='plaintext_encoder',
                      value=ast.Name('plaintext_encoder', ast.Load(), None, None)),
                  ] # keywords
                ) # call
              ) # assign
              if self.cfg.mode == 'aws':
                generated.append(download_ctxt)
              generated.append(assign_init_ctxt)
              generated.append(assign_ciphertext_op)
    #      load_path = node.value.args[0].value + "/" + node.value.args[1].value  
        if self.cfg.mode == 'aws':
          load_path = node.value.args[2]
        else:
          load_path = ast.BinOp(
              left=node.value.args[0],
              op=ast.Add(),
              right=ast.BinOp(
                left=ast.Constant("/",""),
                op=ast.Add(),
                right=node.value.args[1])
          )
        call_load = ast.copy_location(
          ast.Expr(
            ast.Call(
              func=ast.Attribute(
                value=ast.Name(id=node.targets[0].id, ctx=ast.Load(),
                  annotation="", type_comment=""),
                attr='load',
                ctx=ast.Load()),
              args=[load_path],
              keywords=[],)
          ), node
        )
        generated.append(call_load)
        ast.NodeVisitor.generic_visit(self, call_load)
        return generated
      else:
        ast.NodeVisitor.generic_visit(self, node)
        return node
    if isinstance(node.value, ast.Call) and \
       ((isinstance(node.value.func, ast.Attribute) and \
         node.value.func.attr == 'helper')):
      print(node.value.func.attr)
      node.value.args.append(ast.Name('heal', None, None))
      ast.NodeVisitor.generic_visit(self, node)
      return node
#  def 
    
