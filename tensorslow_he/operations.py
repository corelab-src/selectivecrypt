import numpy as np
from tensorslow_he.graph import Operation
from math import pow as mathpow

class add(Operation):
    """Returns x + y element-wise.
    """

    def __init__(self, x, y):
        """Construct add

        Args:
          x: First summand node
          y: Second summand node
        """
        super().__init__([x, y])

    def compute(self, x_value, y_value):
        """Compute the output of the add operation

        Args:
          x_value: First summand value
          y_value: Second summand value
        """
        self.inputs = [x_value, y_value]
        return x_value + y_value


class matmul(Operation):
    """Multiplies matrix a by matrix b, producing a * b.
    """

    def __init__(self, a, b):
        """Construct matmul

        Args:
          a: First matrix
          b: Second matrix
        """
        super().__init__([a, b])

    def compute(self, a_value, b_value):
        """Compute the output of the matmul operation

        Args:
          a_value: First matrix value
          b_value: Second matrix value
        """
        self.inputs = [a_value, b_value]
        return a_value.dot(b_value)

class relu(Operation):
    """Returns the relu of x element-wise.
    """

    def __init__(self, a):
        """Construct relu

        Args:
          a: Input node
        """
        super().__init__([a])

    def compute(self, a_value):
        """Compute the output of the sigmoid operation 
 
        Args:
          a_value: Input value
        """
        a = np.multiply(np.square(a_value), 0.0012)
        b = np.multiply(a_value, 0.5)
        
        return np.add((np.add(a, b)), 52)

class sigmoid(Operation):
    """Returns the sigmoid of x element-wise.
    """

    def __init__(self, a):
        """Construct sigmoid

        Args:
          a: Input node
        """
        super().__init__([a])

    def compute(self, a_value):
        """Compute the output of the sigmoid operation

        Args:
          a_value: Input value
        """
        """
        #from https://eprint.iacr.org/2018/074.pdf section 3.1 taylor polynomial
        const = [0.0208333, 0.00208333, 0.00021081, 0.000021356]
        for i in range(0,len(const)) :
          encrypted_const.append(HE.encryptFrac(const[i]))

        square = np.square(a_value)
        xpow = a_value
        result = np.add(np.multiply(a_value, HE.encryptFrac(0.25)), HE.encryptFrac(0.5))
        
        for n in range(0,5) :
          a = float(pow(-1, n+1))*encrypted_const[n]
          xpow = np.multiply(xpow, square)
          result = result + np.multiply(xpow, HE.encryptFrac(float(a)))
        """
        #from https://eprint.iacr.org/2018/074.pdf section 3.1 fig 3
        const = [0.5, 1.73496, -4.19407, 5.43402, -2.50739]
        encrypted_const = []
        for i in range(0, 5) :
          encrypted_const.append(const[i])
        
        xDiv8 = np.multiply(a_value, 0.125)
        xDiv8square = np.square(xDiv8)
        
        result = np.add(np.multiply(xDiv8, encrypted_const[1]), encrypted_const[0])
        xpow = xDiv8

        for n in range(2,5):
            xpow = np.multiply(xpow, xDiv8square)
            result = result + np.multiply(xpow, encrypted_const[n])

        return result


##no!##
class softmax(Operation):
    """Returns the softmax of a.
    """

    def __init__(self, a):
        """Construct softmax

        Args:
          a: Input node
        """
        super().__init__([a])

    def compute(self, a_value):
        """Compute the output of the softmax operation

        Args:
          a_value: Input value
        """
        const = [0.5, 1.73496, -4.19407, 5.43402, -2.50739]
        encrypted_const = []
        for i in range(0, 5) :
          encrypted_const.append(const[i])
        
        xDiv8 = np.multiply(a_value, 0.125)
        xDiv8square = np.square(xDiv8)
        
        result = np.add(np.multiply(xDiv8, encrypted_const[1]), encrypted_const[0])
        xpow = xDiv8

        for n in range(2,5):
            xpow = np.multiply(xpow, xDiv8square)
            result = result + np.multiply(xpow, encrypted_const[n])

        return result


class log(Operation):
    """Computes the natural logarithm of x element-wise.
    """

    def __init__(self, x):
        """Construct log

        Args:
          x: Input node
        """
        super().__init__([x])

    def compute(self, x_value):
        """Compute the output of the log operation

        Args:
          x_value: Input value
        """
        
        base = np.add(x_value, -1)
        xpow = base
        result = base
        for n in range(2, 10) :
          a = float(mathpow(-1, n+1))/n
          xpow = np.multiply(xpow, base)
          result = result + np.multiply(xpow, a)
  
        return result


class multiply(Operation):
    """Returns x * y element-wise.
    """

    def __init__(self, x, y):
        """Construct multiply

        Args:
          x: First multiplicand node
          y: Second multiplicand node
        """
        super().__init__([x, y])

    def compute(self, x_value, y_value):
        """Compute the output of the multiply operation

        Args:
          x_value: First multiplicand value
          y_value: Second multiplicand value
        """
        #return x_value * y_value
        return np.multiply(x_value, y_value)


class reduce_sum(Operation):
    """Computes the sum of elements across dimensions of a tensor.
    """

    def __init__(self, A, axis=None):
        """Construct reduce_sum

        Args:
          A: The tensor to reduce.
          axis: The dimensions to reduce. If `None` (the default), reduces all dimensions.
        """
        super().__init__([A])
        self.axis = axis

    def compute(self, A_value):
        """Compute the output of the reduce_sum operation

        Args:
          A_value: Input tensor value
        """
        return np.sum(A_value, self.axis)


class negative(Operation):
    """Computes the negative of x element-wise.
    """

    def __init__(self, x):
        """Construct negative

        Args:
          x: Input node
        """
        super().__init__([x])

    def compute(self, x_value):
        """Compute the output of the negative operation

        Args:
          x_value: Input value
        """
        
        zero = 0.0
         
        return np.subtract(zero, x_value)
        
class pow(Operation):
    """Computes the negative of x element-wise.
    """

    def __init__(self, x, y):
        """Construct negativea

        Args:
          x: Input node
        """
        super().__init__([x, y])

    def compute(self, x_value, y_value):
        """Compute the output of the negative operation

        Args:
          x_value: Input value
        """
        if y_value == 0 :
          return np.array([])
        
        result = x_value
        for i in (1, y_value) :
          result = np.multiply(result, x_value)
        
        return result
        
class div(Operation):
    """Computes the negative of x element-wise.
    """

    def __init__(self, x, y):
        """Construct negative

        Args:
          x: Input node
        """
        super().__init__([x, y])

    def compute(self, x_value, y_value):
        """Compute the output of the negative operation

        Args:
          x_value: Input value
        """
        #return -x_value
        divider = 1/float(y_value)
        return np.multiply(x_value, divider)

class reduce_mean(Operation):
    """Computes the sum of elements across dimensions of a tensor.
    """

    def __init__(self, A, axis=None):
        """Construct reduce_sum

        Args:
          A: The tensor to reduce.
          axis: The dimensions to reduce. If `None` (the default), reduces all dimensions.
        """
        super().__init__([A])
        self.axis = axis

    def compute(self, A_value):
        """Compute the output of the reduce_sum operation

        Args:
          A_value: Input tensor value
        """
      
        size = 1/float(A_value.size)
        return  np.multiply(np.sum(A_value, self.axis), size)
