const express = require('express');
const router = express.Router();
const validateEmployeeWithZod = require('../middleware/validateEmployee');
const {
  getAllEmployees,
  getEmployeeById,
  createEmployee,
  updateEmployee,
  deleteEmployee,
} = require('../controllers/employeeController');

router
  .route('/')
  .get(getAllEmployees)
  .post(validateEmployeeWithZod, createEmployee);

router
  .route('/:id')
  .get(getEmployeeById)
  .put(validateEmployeeWithZod, updateEmployee)
  .delete(deleteEmployee);

module.exports = router;
