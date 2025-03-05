from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from .models import Department, Position, EducationLevel, Employee, EmploymentContract, InsuranceAndTax
from .forms import DepartmentForm, PositionForm, EducationLevelForm, EmployeeForm
import datetime
from django.utils import timezone
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ModelTestCase(TestCase):
    """Test cases for the models in the employees app"""
    
    def setUp(self):
        # Create test data for models
        self.department = Department.objects.create(
            department_name="Test Department",
            department_code="1234",
            description="Test department description",
            status=True
        )
        
        self.position = Position.objects.create(
            position_name="Test Position",
            position_code="5678",
            description="Test position description",
            status=True
        )
        
        self.education = EducationLevel.objects.create(
            education_name="Test Education",
            education_code="9012",
            description="Test education description"
        )
        
        self.employee = Employee.objects.create(
            full_name="Test Employee",
            gender="Male",
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365*30),
            id_card="123456789012",
            email="test@example.com",
            phone="1234567890",
            address="Test Address",
            department=self.department,
            position=self.position,
            education=self.education,
            hire_date=timezone.now().date() - datetime.timedelta(days=365),
            status="Working"
        )
        
        self.contract = EmploymentContract.objects.create(
            employee=self.employee,
            contract_type="Fixed Term",
            start_date=timezone.now().date() - datetime.timedelta(days=365),
            end_date=timezone.now().date() + datetime.timedelta(days=365),
            base_salary=Decimal('10000000'),
            allowance=Decimal('2000000'),
            sign_date=timezone.now().date() - datetime.timedelta(days=370),
            signed_by="Test HR Manager",
            status="Active"
        )
        
        self.insurance = InsuranceAndTax.objects.create(
            employee=self.employee,
            social_insurance_number="1234567890",
            social_insurance_date=timezone.now().date() - datetime.timedelta(days=350),
            social_insurance_place="Test Social Insurance Office",
            health_insurance_number="0987654321",
            health_insurance_date=timezone.now().date() - datetime.timedelta(days=350),
            health_insurance_place="Test Health Insurance Office",
            tax_code="1234509876",
            status="Active"
        )
    
    def test_department_str(self):
        """Test the string representation of Department model"""
        self.assertEqual(str(self.department), "Test Department")
    
    def test_position_str(self):
        """Test the string representation of Position model"""
        self.assertEqual(str(self.position), "Test Position")
    
    def test_education_str(self):
        """Test the string representation of EducationLevel model"""
        self.assertEqual(str(self.education), "Test Education")
    
    def test_employee_str(self):
        """Test the string representation of Employee model"""
        self.assertEqual(str(self.employee), "Test Employee")
    
    def test_contract_str(self):
        """Test the string representation of EmploymentContract model"""
        expected = f"Contract for {self.employee.full_name} - {self.contract.contract_type}"
        self.assertEqual(str(self.contract), expected)
    
    def test_insurance_str(self):
        """Test the string representation of InsuranceAndTax model"""
        expected = f"Insurance for {self.employee.full_name}"
        self.assertEqual(str(self.insurance), expected)
    
    def test_department_active_filter(self):
        """Test filtering departments by active status"""
        inactive_dept = Department.objects.create(
            department_name="Inactive Department",
            department_code="9999",
            status=False
        )
        active_depts = Department.objects.filter(status=True)
        self.assertIn(self.department, active_depts)
        self.assertNotIn(inactive_dept, active_depts)
    
    def test_employee_age_calculation(self):
        """Test the age calculation for an employee"""
        # Assuming Employee model has an age property or method
        if hasattr(self.employee, 'age'):
            expected_age = 30  # Based on the DOB set in setUp
            self.assertEqual(self.employee.age, expected_age)
    
    def test_contract_duration_calculation(self):
        """Test the contract duration calculation"""
        # Assuming EmploymentContract model has a duration property or method
        if hasattr(self.contract, 'duration'):
            expected_duration = 730  # 2 years in days
            self.assertEqual(self.contract.duration, expected_duration)


class FormTestCase(TestCase):
    """Test cases for forms in the employees app"""
    
    def setUp(self):
        # Create test data for form validation
        self.department = Department.objects.create(
            department_name="Existing Department",
            department_code="1234",
            status=True
        )
        
        self.position = Position.objects.create(
            position_name="Existing Position",
            position_code="5678",
            status=True
        )
        
        self.education = EducationLevel.objects.create(
            education_name="Existing Education",
            education_code="9012"
        )
    
    def test_department_form_valid(self):
        """Test valid department form"""
        form_data = {
            'department_name': 'New Department',
            'department_code': '9876',
            'description': 'New department description',
            'status': True
        }
        form = DepartmentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_department_form_duplicate_code(self):
        """Test department form with duplicate code"""
        form_data = {
            'department_name': 'Another Department',
            'department_code': '1234',  # Same as existing department
            'status': True
        }
        form = DepartmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('department_code', form.errors)
    
    def test_position_form_valid(self):
        """Test valid position form"""
        form_data = {
            'position_name': 'New Position',
            'position_code': '4321',
            'description': 'New position description',
            'status': True
        }
        form = PositionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_education_form_valid(self):
        """Test valid education form"""
        form_data = {
            'education_name': 'New Education',
            'education_code': '3456',
            'description': 'New education description'
        }
        form = EducationLevelForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_employee_form_valid(self):
        """Test valid employee form"""
        form_data = {
            'full_name': 'New Employee',
            'gender': 'Male',
            'date_of_birth': '1990-01-01',
            'id_card': '123456789012',
            'email': 'new@example.com',
            'phone': '0987654321',
            'address': 'New Address',
            'department': self.department.id,
            'position': self.position.id,
            'education': self.education.id,
            'hire_date': '2022-01-01',
            'status': 'Working'
        }
        
        # Create a simple image file for testing
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # Empty content for simplicity
            content_type='image/jpeg'
        )
        
        form = EmployeeForm(data=form_data, files={'profile_image': image})
        
        if not form.is_valid():
            print(form.errors)  # Print errors for debugging
            
        self.assertTrue(form.is_valid())


class ViewTestCase(TestCase):
    """Test cases for views in the employees app"""
    
    def setUp(self):
        # Create a test user with necessary permissions
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create permissions
        content_type = ContentType.objects.get_for_model(User)
        
        view_perm = Permission.objects.create(
            codename='view_employee_data',
            name='Can view employee data',
            content_type=content_type,
        )
        
        add_perm = Permission.objects.create(
            codename='add_employee_data',
            name='Can add employee data',
            content_type=content_type,
        )
        
        change_perm = Permission.objects.create(
            codename='change_employee_data',
            name='Can change employee data',
            content_type=content_type,
        )
        
        delete_perm = Permission.objects.create(
            codename='delete_employee_data',
            name='Can delete employee data',
            content_type=content_type,
        )
        
        # Create a group and add permissions
        self.group = Group.objects.create(name='HR')
        self.group.permissions.add(view_perm, add_perm, change_perm, delete_perm)
        
        # Add user to group
        self.user.groups.add(self.group)
        
        # Create test data
        self.department = Department.objects.create(
            department_name="Test Department",
            department_code="1234",
            status=True
        )
        
        self.position = Position.objects.create(
            position_name="Test Position",
            position_code="5678",
            status=True
        )
        
        self.education = EducationLevel.objects.create(
            education_name="Test Education",
            education_code="9012"
        )
        
        self.employee = Employee.objects.create(
            full_name="Test Employee",
            gender="Male",
            date_of_birth=timezone.now().date() - datetime.timedelta(days=365*30),
            id_card="123456789012",
            email="test@example.com",
            phone="1234567890",
            address="Test Address",
            department=self.department,
            position=self.position,
            education=self.education,
            hire_date=timezone.now().date() - datetime.timedelta(days=365),
            status="Working"
        )
        
        # Set up the test client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_department_list_view(self):
        """Test department list view"""
        url = reverse('department_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/departments/department_list.html')
        self.assertIn('departments', response.context)
        self.assertIn(self.department, response.context['departments'])
    
    def test_department_create_view(self):
        """Test department create view"""
        url = reverse('department_create')
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/departments/department_form.html')
        self.assertIn('form', response.context)
        
        # Test POST request
        post_data = {
            'department_name': 'New Department',
            'department_code': '9876',
            'description': 'New department description',
            'status': True
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check if department was created
        self.assertTrue(Department.objects.filter(department_name='New Department').exists())
    
    def test_department_edit_view(self):
        """Test department edit view"""
        url = reverse('department_edit', args=[self.department.id])
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/departments/department_form.html')
        self.assertIn('form', response.context)
        
        # Test POST request
        post_data = {
            'department_name': 'Updated Department',
            'department_code': self.department.department_code,
            'description': 'Updated description',
            'status': True
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Check if department was updated
        self.department.refresh_from_db()
        self.assertEqual(self.department.department_name, 'Updated Department')
    
    def test_department_delete_view(self):
        """Test department delete view"""
        url = reverse('department_delete', args=[self.department.id])
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/departments/department_confirm_delete.html')
        
        # Test POST request
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after successful deletion
        
        # Check if department was deleted
        self.assertFalse(Department.objects.filter(id=self.department.id).exists())
    
    def test_employee_list_view(self):
        """Test employee list view"""
        url = reverse('employee_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/employee_list.html')
        self.assertIn('employees', response.context)
        self.assertIn(self.employee, response.context['employees'])
    
    def test_employee_detail_view(self):
        """Test employee detail view"""
        url = reverse('employee_detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'employees/employee_detail.html')
        self.assertIn('employee', response.context)
        self.assertEqual(response.context['employee'], self.employee)
    
    def test_employee_filter(self):
        """Test employee filtering"""
        url = reverse('employee_list') + f'?department={self.department.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.employee, response.context['employees'])
        
        # Test filtering by non-existent department
        url = reverse('employee_list') + '?department=999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.employee, response.context['employees'])


class IntegrationTestCase(TestCase):
    """Integration tests for the employees app"""
    
    def setUp(self):
        # Create a test user with necessary permissions
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create permissions
        content_type = ContentType.objects.get_for_model(User)
        
        view_perm = Permission.objects.create(
            codename='view_employee_data',
            name='Can view employee data',
            content_type=content_type,
        )
        
        add_perm = Permission.objects.create(
            codename='add_employee_data',
            name='Can add employee data',
            content_type=content_type,
        )
        
        view_contract_perm = Permission.objects.create(
            codename='view_contract',
            name='Can view contract',
            content_type=content_type,
        )
        
        add_contract_perm = Permission.objects.create(
            codename='add_contract',
            name='Can add contract',
            content_type=content_type,
        )
        
        # Create a group and add permissions
        self.group = Group.objects.create(name='HR')
        self.group.permissions.add(view_perm, add_perm, view_contract_perm, add_contract_perm)
        
        # Add user to group
        self.user.groups.add(self.group)
        
        # Set up the test client
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
    
    def test_create_employee_and_contract_flow(self):
        """Test the full flow of creating an employee and then a contract"""
        # First create a department
        dept_data = {
            'department_name': 'Integration Test Department',
            'department_code': '1111',
            'description': 'Department for integration testing',
            'status': True
        }
        dept_url = reverse('department_create')
        response = self.client.post(dept_url, dept_data)
        self.assertEqual(response.status_code, 302)
        department = Department.objects.get(department_name='Integration Test Department')
        
        # Then create a position
        pos_data = {
            'position_name': 'Integration Test Position',
            'position_code': '2222',
            'description': 'Position for integration testing',
            'status': True
        }
        pos_url = reverse('position_create')
        response = self.client.post(pos_url, pos_data)
        self.assertEqual(response.status_code, 302)
        position = Position.objects.get(position_name='Integration Test Position')
        
        # Then create an education level
        edu_data = {
            'education_name': 'Integration Test Education',
            'education_code': '3333',
            'description': 'Education for integration testing'
        }
        edu_url = reverse('education_create')
        response = self.client.post(edu_url, edu_data)
        self.assertEqual(response.status_code, 302)
        education = EducationLevel.objects.get(education_name='Integration Test Education')
        
        # Now create an employee
        emp_data = {
            'full_name': 'Integration Test Employee',
            'gender': 'Male',
            'date_of_birth': '1990-01-01',
            'id_card': '123456789012',
            'email': 'integration@example.com',
            'phone': '0987654321',
            'address': 'Integration Test Address',
            'department': department.id,
            'position': position.id,
            'education': education.id,
            'hire_date': '2022-01-01',
            'status': 'Working'
        }
        emp_url = reverse('employee_create')
        response = self.client.post(emp_url, emp_data)
        self.assertEqual(response.status_code, 302)
        employee = Employee.objects.get(full_name='Integration Test Employee')
        
        # Finally create a contract for the employee
        contract_data = {
            'employee': employee.id,
            'contract_type': 'Fixed Term',
            'start_date': '2022-01-01',
            'end_date': '2023-01-01',
            'base_salary': '10000000',
            'allowance': '2000000',
            'sign_date': '2021-12-25',
            'signed_by': 'Integration Test HR Manager',
            'status': 'Active'
        }
        contract_url = reverse('contract_create')
        response = self.client.post(contract_url, contract_data)
        self.assertEqual(response.status_code, 302)
        
        # Check if contract was created
        self.assertTrue(EmploymentContract.objects.filter(employee=employee).exists())
        
        # Check the employee detail page includes the contract
        detail_url = reverse('employee_detail', args=[employee.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('contracts', response.context)
        self.assertEqual(len(response.context['contracts']), 1)


if __name__ == '__main__':
    import unittest
    unittest.main()
