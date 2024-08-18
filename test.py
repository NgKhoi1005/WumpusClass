from pysat.formula import CNF, IDPool
from pysat.solvers import Solver

KB = CNF()
vpool = IDPool()

from pysat.solvers import Solver

# Tạo một solver
solver = Solver()

# Thêm mệnh đề vào solver
solver.add_clause([-1, -2])  # Biến 1 phải là False
solver.add_clause([1])  # Biến 1 phải là False

# Giải bài toán
is_satisfiable = solver.solve()

# Kiểm tra xem bài toán có giải được không
if is_satisfiable:
    print("Có thể giải quyết được vấn đề. Đây là một lời giải hợp lệ.")
    model = solver.get_model()
    print("Lời giải: ", model)
else:
    print("Không thể giải quyết vấn đề. Không có lời giải hợp lệ.")
