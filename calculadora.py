import numpy as np
import dearpygui.dearpygui as dpg

class MatrixApp:
    def __init__(self):
        self.dimA = (2, 2)
        self.dimB = (2, 2)
        self.A = np.zeros(self.dimA)
        self.B = np.zeros(self.dimB)
        self.result = None

        dpg.create_context()
        self.build_layout()
        dpg.set_primary_window("MainWindow", True)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def build_layout(self):
        dpg.create_viewport(title="Calculadora de Matrizes", width=1350, height=700)
        with dpg.window(tag="MainWindow", label="Calculadora de Matrizes", width=-1, height=-1):

            with dpg.group(horizontal=True):
                # MENU LATERAL
                with dpg.child_window(width=300):
                    dpg.add_text("Configurações", color=(0, 200, 255))

                    dpg.add_text("Matriz A:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_int(label="Linhas", tag="rows_A", default_value=self.dimA[0], min_value=1, width=80)
                        dpg.add_input_int(label="Cols", tag="cols_A", default_value=self.dimA[1], min_value=1, width=80)

                    dpg.add_text("Matriz B:")
                    with dpg.group(horizontal=True):
                        dpg.add_input_int(label="Linhas", tag="rows_B", default_value=self.dimB[0], min_value=1, width=80)
                        dpg.add_input_int(label="Cols", tag="cols_B", default_value=self.dimB[1], min_value=1, width=80)

                    dpg.add_button(label="Definir Dimensões", callback=self.update_dimensions, width=230)
                    dpg.add_spacer(height=10)
                    dpg.add_button(label="Calcular A × B", callback=self.calculate_ab, width=230)
                    dpg.add_button(label="Calcular B × A", callback=self.calculate_ba, width=230)
                    dpg.add_button(label="Limpar Tudo", callback=self.clear_all, width=230)
                    dpg.add_button(label="Sair", callback=lambda: dpg.stop_dearpygui(), width=230)

                # MATRIZES E RESULTADO
                with dpg.group():
                    with dpg.group(horizontal=True):
                        with dpg.child_window(width=500, height=300, horizontal_scrollbar=True):
                            dpg.add_button(label="Identidade A", callback=lambda: self.fill_identity("A"), width=120)
                            dpg.add_text("Matriz A", color=(100, 200, 255))
                            self.table_A = dpg.add_table(header_row=False, tag="table_A",
                                                         borders_innerH=True, borders_outerH=True,
                                                         borders_innerV=True, borders_outerV=True)
                            self.update_matrix_table("A", self.A)

                        with dpg.child_window(width=500, height=300, horizontal_scrollbar=True):
                            dpg.add_button(label="Identidade B", callback=lambda: self.fill_identity("B"), width=120)
                            dpg.add_text("Matriz B", color=(100, 200, 255))
                            self.table_B = dpg.add_table(header_row=False, tag="table_B",
                                                         borders_innerH=True, borders_outerH=True,
                                                         borders_innerV=True, borders_outerV=True)
                            self.update_matrix_table("B", self.B)

                    with dpg.child_window(width=1010, height=-1):
                        dpg.add_text("Resultado", color=(100, 255, 150))
                        self.result_display = dpg.add_input_text(
                            multiline=True, readonly=True,
                            tag="result_display", width=-1, height=-1
                        )

            # Popup de erro
            with dpg.window(modal=True, show=False, tag="error_popup", no_title_bar=False, autosize=True):
                dpg.add_text("", tag="error_text")
                dpg.add_button(label="Fechar", callback=lambda: dpg.configure_item("error_popup", show=False))

    def show_error(self, message):
        dpg.set_value("error_text", message)
        dpg.configure_item("error_popup", show=True)

    def update_matrix_table(self, prefix, matrix):
        table_tag = f"table_{prefix}"
        dpg.delete_item(table_tag, children_only=True)
        for _ in range(matrix.shape[1]):
            dpg.add_table_column(parent=table_tag)
        for i in range(matrix.shape[0]):
            with dpg.table_row(parent=table_tag):
                for j in range(matrix.shape[1]):
                    dpg.add_input_float(
                        width=80, step=0.0,
                        default_value=matrix[i, j],
                        tag=f"{prefix}_{i}_{j}",
                        format="%.2f"
                    )

    def update_dimensions(self):
        try:
            rows_A = dpg.get_value("rows_A")
            cols_A = dpg.get_value("cols_A")
            rows_B = dpg.get_value("rows_B")
            cols_B = dpg.get_value("cols_B")
            
            if cols_A <= 0 or cols_B <= 0 or rows_A <= 0 or rows_B <= 0:
                self.show_error("Dimensões inválidas! Apenas números inteiros positivos!")
                return
            
            self.dimA = (rows_A, cols_A)
            self.dimB = (rows_B, cols_B)
            self.A = np.zeros(self.dimA)
            self.B = np.zeros(self.dimB)
            self.update_matrix_table("A", self.A)
            self.update_matrix_table("B", self.B)

            dpg.set_value("result_display", "Dimensões atualizadas com sucesso!")
        except Exception as e:
            self.show_error(f"Erro ao atualizar dimensões: {str(e)}")

    def calculate_ab(self):
        try:
            for i in range(self.dimA[0]):
                for j in range(self.dimA[1]):
                    self.A[i, j] = dpg.get_value(f"A_{i}_{j}")
            for i in range(self.dimB[0]):
                for j in range(self.dimB[1]):
                    self.B[i, j] = dpg.get_value(f"B_{i}_{j}")

            if self.dimA[1] != self.dimB[0]:
                raise ValueError("Para A × B: número de colunas de A deve ser igual ao número de linhas de B.")

            self.result = np.matmul(self.A, self.B)

            result_str = "Resultado (A × B):\n\n"
            result_str += '\n'.join(['  '.join([f"{num:8.2f}" for num in row]) for row in self.result])
            result_str += f"\n\nDimensões: {self.result.shape[0]}x{self.result.shape[1]}"

            dpg.set_value("result_display", result_str)
        except Exception as e:
            self.show_error(str(e))

    def calculate_ba(self):
        try:
            for i in range(self.dimA[0]):
                for j in range(self.dimA[1]):
                    self.A[i, j] = dpg.get_value(f"A_{i}_{j}")
            for i in range(self.dimB[0]):
                for j in range(self.dimB[1]):
                    self.B[i, j] = dpg.get_value(f"B_{i}_{j}")

            if self.dimB[1] != self.dimA[0]:
                raise ValueError("Para B × A: número de colunas de B deve ser igual ao número de linhas de A.")

            self.result = np.matmul(self.B, self.A)

            result_str = "Resultado (B × A):\n\n"
            result_str += '\n'.join(['  '.join([f"{num:8.2f}" for num in row]) for row in self.result])
            result_str += f"\n\nDimensões: {self.result.shape[0]}x{self.result.shape[1]}"

            dpg.set_value("result_display", result_str)
        except Exception as e:
            self.show_error(str(e))

    def fill_identity(self, prefix):
        try:
            if prefix == "A":
                rows, cols = self.dimA
            else:
                rows, cols = self.dimB
            size = min(rows, cols)
            for i in range(rows):
                for j in range(cols):
                    val = 1.0 if i == j and i < size else 0.0
                    dpg.set_value(f"{prefix}_{i}_{j}", val)
        except Exception as e:
            self.show_error(f"Erro ao preencher identidade: {str(e)}")

    def clear_all(self):
        self.A = np.zeros(self.dimA)
        self.B = np.zeros(self.dimB)
        self.result = None
        for i in range(self.dimA[0]):
            for j in range(self.dimA[1]):
                dpg.set_value(f"A_{i}_{j}", 0.0)
        for i in range(self.dimB[0]):
            for j in range(self.dimB[1]):
                dpg.set_value(f"B_{i}_{j}", 0.0)
        dpg.set_value("result_display", "")

if __name__ == "__main__":
    MatrixApp()
