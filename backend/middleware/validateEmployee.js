const { z } = require('zod');

const employeeZodSchema = z.object({
  fullName: z
    .string({ required_error: 'Full name is required' })
    .trim()
    .min(1, 'Full name is required')
    .regex(/^[A-Za-z\s]+$/, 'Full name must contain only letters and spaces (no numbers or special characters)'),

  employeeId: z
    .string({ required_error: 'Employee ID is required' })
    .trim()
    .min(1, 'Employee ID is required')
    .regex(/^EMP\d+$/, 'Employee ID must start with capital EMP followed by numbers (e.g. EMP001)'),

  email: z
    .string({ required_error: 'Email is required' })
    .trim()
    .toLowerCase()
    .min(1, 'Email is required')
    .email('Invalid email format')
    .regex(/^[a-z0-9._%+-]+@snsgroups\.com$/, 'Email must end with @snsgroups.com domain'),

  phone: z
    .string({ required_error: 'Phone number is required' })
    .trim()
    .min(1, 'Phone number is required')
    .regex(/^\d{10}$/, 'Phone number must be exactly 10 digits'),

  dateOfBirth: z.string().optional().nullable(),
  gender: z.enum(['Male', 'Female', 'Other', '']).optional().nullable(),
  address: z.string().trim().max(500, 'Address cannot exceed 500 characters').optional().nullable(),
  department: z.enum(['IT', 'HR', 'Finance', 'Marketing', 'Operations', 'Sales', 'Admin', 'Other', '']).optional().nullable(),
  position: z.string().trim().max(100, 'Position cannot exceed 100 characters').optional().nullable(),
  joinDate: z.string().optional().nullable(),
});

/**
 * Express middleware to validate request body using Zod schema
 */
const validateEmployeeWithZod = (req, res, next) => {
  const result = employeeZodSchema.safeParse(req.body);
  if (!result.success) {
    const errorMessages = result.error.issues.map((issue) => issue.message);
    return res.status(400).json({
      success: false,
      message: errorMessages.join(', '),
      errors: result.error.format(),
    });
  }
  // Replace req.body with sanitized & type-safe Zod data
  req.body = result.data;
  next();
};

module.exports = validateEmployeeWithZod;
