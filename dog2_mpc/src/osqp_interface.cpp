#include "dog2_mpc/osqp_interface.hpp"
#include <iostream>
#include <cstring>
#include <cstdlib>

namespace dog2_mpc {

OSQPInterface::OSQPInterface()
    : solver_(nullptr),
      settings_(nullptr),
      initialized_(false),
      n_(0),
      m_(0),
      P_csc_(nullptr),
      A_csc_(nullptr),
      last_status_(-1),
      last_solve_time_(0.0),
      last_iterations_(0),
      last_obj_val_(0.0) {
}

OSQPInterface::~OSQPInterface() {
    cleanup();
}

bool OSQPInterface::setup(const Eigen::MatrixXd& P,
                         const Eigen::VectorXd& q,
                         const Eigen::MatrixXd& A,
                         const Eigen::VectorXd& l,
                         const Eigen::VectorXd& u) {
    // 转换为稀疏矩阵
    Eigen::SparseMatrix<double> P_sparse = P.sparseView();
    Eigen::SparseMatrix<double> A_sparse = A.sparseView();
    
    return setup(P_sparse, q, A_sparse, l, u);
}

bool OSQPInterface::setup(const Eigen::SparseMatrix<double>& P,
                         const Eigen::VectorXd& q,
                         const Eigen::SparseMatrix<double>& A,
                         const Eigen::VectorXd& l,
                         const Eigen::VectorXd& u) {
    // 清理之前的求解器
    if (initialized_) {
        cleanup();
    }
    
    // 检查维度
    n_ = q.size();
    m_ = l.size();
    
    if (P.rows() != n_ || P.cols() != n_) {
        std::cerr << "Error: P matrix dimension mismatch" << std::endl;
        return false;
    }
    
    if (A.rows() != m_ || A.cols() != n_) {
        std::cerr << "Error: A matrix dimension mismatch" << std::endl;
        return false;
    }
    
    if (u.size() != m_) {
        std::cerr << "Error: u vector dimension mismatch" << std::endl;
        return false;
    }
    
    // 转换为CSC格式
    P_csc_ = eigenToCSC(P);
    A_csc_ = eigenToCSC(A);
    
    // 复制向量数据
    q_data_.resize(n_);
    l_data_.resize(m_);
    u_data_.resize(m_);
    
    for (int i = 0; i < n_; ++i) {
        q_data_[i] = q(i);
    }
    for (int i = 0; i < m_; ++i) {
        l_data_[i] = l(i);
        u_data_[i] = u(i);
    }
    
    // 设置OSQP设置
    settings_ = (OSQPSettings*)malloc(sizeof(OSQPSettings));
    if (!settings_) {
        std::cerr << "Error: Failed to allocate OSQPSettings" << std::endl;
        return false;
    }
    
    osqp_set_default_settings(settings_);
    settings_->verbose = 0;
    settings_->warm_starting = 1;
    settings_->max_iter = 4000;
    settings_->eps_abs = 1e-4;
    settings_->eps_rel = 1e-4;
    
    // 初始化求解器 - OSQP 0.6.3 API
    OSQPInt exitflag = osqp_setup(&solver_, 
                                   P_csc_, 
                                   q_data_.data(),
                                   A_csc_, 
                                   l_data_.data(), 
                                   u_data_.data(),
                                   m_, 
                                   n_, 
                                   settings_);
    
    if (exitflag != 0) {
        std::cerr << "Error: OSQP setup failed with code " << exitflag << std::endl;
        return false;
    }
    
    initialized_ = true;
    return true;
}

bool OSQPInterface::solve(Eigen::VectorXd& solution) {
    if (!initialized_) {
        std::cerr << "Error: OSQP not initialized" << std::endl;
        return false;
    }
    
    // 求解 - OSQP 0.6.3 API
    OSQPInt exitflag = osqp_solve(solver_);
    
    if (exitflag != 0) {
        std::cerr << "Error: OSQP solve failed with code " << exitflag << std::endl;
        return false;
    }
    
    // 提取解
    solution.resize(n_);
    for (OSQPInt i = 0; i < n_; ++i) {
        solution(i) = solver_->solution->x[i];
    }
    
    // 保存统计信息
    last_status_ = solver_->info->status_val;
    last_solve_time_ = solver_->info->solve_time * 1000.0;
    last_iterations_ = solver_->info->iter;
    last_obj_val_ = solver_->info->obj_val;
    
    return (last_status_ == OSQP_SOLVED || last_status_ == OSQP_SOLVED_INACCURATE);
}

void OSQPInterface::cleanup() {
    if (solver_) {
        osqp_cleanup(solver_);
        solver_ = nullptr;
    }
    
    if (settings_) {
        free(settings_);
        settings_ = nullptr;
    }
    
    if (P_csc_) {
        OSQPCscMatrix_free(P_csc_);
        P_csc_ = nullptr;
    }
    
    if (A_csc_) {
        OSQPCscMatrix_free(A_csc_);
        A_csc_ = nullptr;
    }
    
    initialized_ = false;
}

OSQPCscMatrix* OSQPInterface::eigenToCSC(const Eigen::SparseMatrix<double>& mat) {
    OSQPInt rows = mat.rows();
    OSQPInt cols = mat.cols();
    OSQPInt nnz = mat.nonZeros();
    
    OSQPFloat* x = (OSQPFloat*)malloc(nnz * sizeof(OSQPFloat));
    OSQPInt* i = (OSQPInt*)malloc(nnz * sizeof(OSQPInt));
    OSQPInt* p = (OSQPInt*)malloc((cols + 1) * sizeof(OSQPInt));
    
    OSQPInt idx = 0;
    for (OSQPInt k = 0; k < cols; ++k) {
        p[k] = idx;
        for (Eigen::SparseMatrix<double>::InnerIterator it(mat, k); it; ++it) {
            x[idx] = it.value();
            i[idx] = it.row();
            ++idx;
        }
    }
    p[cols] = nnz;
    
    OSQPCscMatrix* result = OSQPCscMatrix_new(rows, cols, nnz, x, i, p);
    if (result) {
        result->owned = 1;
    }
    
    return result;
}

int OSQPInterface::getStatus() const {
    return last_status_;
}

double OSQPInterface::getSolveTime() const {
    return last_solve_time_;
}

int OSQPInterface::getIterations() const {
    return last_iterations_;
}

double OSQPInterface::getObjectiveValue() const {
    return last_obj_val_;
}

} // namespace dog2_mpc
