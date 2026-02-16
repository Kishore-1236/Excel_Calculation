import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import StudentMarks
import json


def index(request):
    """Render the upload page"""
    return render(request, 'index.html')


@require_http_methods(["POST"])
def get_sheets(request):
    """Get list of sheets from uploaded Excel file"""
    if 'excel_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    excel_file = request.FILES['excel_file']
    
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return JsonResponse({'error': 'Invalid file format'}, status=400)
    
    try:
        # Read all sheet names
        xls = pd.ExcelFile(excel_file)
        sheets = xls.sheet_names
        return JsonResponse({'sheets': sheets, 'filename': excel_file.name})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def get_columns(request):
    """Get column preview from uploaded Excel file"""
    if 'excel_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    excel_file = request.FILES['excel_file']
    sheet_name = request.POST.get('sheet_name', 0)
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
        
        # Get first 10 rows for preview
        preview_data = []
        for idx, row in df.head(10).iterrows():
            preview_data.append({
                'row_num': idx,
                'values': [str(val) if pd.notna(val) else '' for val in row]
            })
        
        # Get column count
        num_columns = len(df.columns)
        
        return JsonResponse({
            'preview': preview_data,
            'num_columns': num_columns,
            'column_letters': [chr(65 + i) for i in range(min(num_columns, 26))]  # A-Z
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def parse_mark_value(value):
    """Parse a mark value, return None if empty or NaN"""
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return int(float(value))  # Convert to float first, then to int
    except (ValueError, TypeError):
        return None


@require_http_methods(["POST"])
def upload_excel(request):
    """Handle Excel file upload and save to database"""
    if 'excel_file' not in request.FILES:
        messages.error(request, 'Please select a file to upload.')
        return redirect('index')
    
    excel_file = request.FILES['excel_file']
    sheet_name = request.POST.get('sheet_name', 0)
    semester = request.POST.get('semester', '')
    batch = request.POST.get('batch', '')
    subject_name = request.POST.get('subject_name', '')
    
    # Get column mappings (-1 means skip/null)
    header_row = int(request.POST.get('header_row', 0))
    data_start_row = int(request.POST.get('data_start_row', 1))
    col_sno = int(request.POST.get('col_sno', 0))
    col_regno = int(request.POST.get('col_regno', 1))
    
    # All mark columns (can be -1 for skip)
    col_m1q1a = int(request.POST.get('col_m1q1a', -1))
    col_m1q1b = int(request.POST.get('col_m1q1b', -1))
    col_m1q2a = int(request.POST.get('col_m1q2a', -1))
    col_m1q2b = int(request.POST.get('col_m1q2b', -1))
    col_m1q3a = int(request.POST.get('col_m1q3a', -1))
    col_m1q3b = int(request.POST.get('col_m1q3b', -1))
    col_m1qu1 = int(request.POST.get('col_m1qu1', -1))
    col_m1a1 = int(request.POST.get('col_m1a1', -1))
    col_m2q1a = int(request.POST.get('col_m2q1a', -1))
    col_m2q1b = int(request.POST.get('col_m2q1b', -1))
    col_m2q2a = int(request.POST.get('col_m2q2a', -1))
    col_m2q2b = int(request.POST.get('col_m2q2b', -1))
    col_m2q3a = int(request.POST.get('col_m2q3a', -1))
    col_m2q3b = int(request.POST.get('col_m2q3b', -1))
    col_m2qu2 = int(request.POST.get('col_m2qu2', -1))
    col_m2a2 = int(request.POST.get('col_m2a2', -1))
    
    # Validate required fields
    if not semester or not batch:
        messages.error(request, 'Please provide semester and batch.')
        return redirect('index')
    
    # Validate file type
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        messages.error(request, 'Invalid file format. Please upload an Excel file (.xlsx or .xls).')
        return redirect('index')
    
    try:
        # Check if all sheets should be processed
        process_all_sheets = (sheet_name == '__ALL_SHEETS__')
        
        if process_all_sheets:
            xls = pd.ExcelFile(excel_file)
            sheets_to_process = xls.sheet_names
        else:
            sheets_to_process = [sheet_name]
        
        # Helper function to get value from column (returns None if column is -1 or out of range)
        def get_col_value(row, col_idx):
            if col_idx == -1 or col_idx >= len(row):
                return None
            return parse_mark_value(row[col_idx])
        
        total_records_created = 0
        sheets_processed = 0
        subjects_uploaded = []
        
        for current_sheet in sheets_to_process:
            try:
                # Use sheet name as subject name
                current_subject = current_sheet
                
                # Read Excel file from current sheet
                df = pd.read_excel(excel_file, sheet_name=current_sheet, header=None)
                
                # Skip to data start row
                df = df.iloc[data_start_row:].reset_index(drop=True)
                
                # Remove rows with empty S.No
                df = df.dropna(subset=[col_sno])
                df = df[df[col_sno] != '']
                
                # Filter out non-numeric S.No (like "No of Absents", "Signature", etc.)
                def is_valid_sno(val):
                    try:
                        int(val)
                        return True
                    except (ValueError, TypeError):
                        return False
                
                df = df[df[col_sno].apply(is_valid_sno)]
                
                # Clear existing data for this combination
                StudentMarks.objects.filter(
                    semester=semester,
                    batch=batch,
                    subject_name=current_subject
                ).delete()
                
                records_created = 0
                for _, row in df.iterrows():
                    try:
                        StudentMarks.objects.create(
                            semester=semester,
                            batch=batch,
                            subject_name=current_subject,
                            s_no=int(row[col_sno]) if pd.notna(row[col_sno]) else 0,
                            regd_no=str(row[col_regno]) if pd.notna(row[col_regno]) else '',
                            
                            # MID I marks
                            m1q1a=get_col_value(row, col_m1q1a),
                            m1q1b=get_col_value(row, col_m1q1b),
                            m1q2a=get_col_value(row, col_m1q2a),
                            m1q2b=get_col_value(row, col_m1q2b),
                            m1q3a=get_col_value(row, col_m1q3a),
                            m1q3b=get_col_value(row, col_m1q3b),
                            m1qu1=get_col_value(row, col_m1qu1),
                            m1a1=get_col_value(row, col_m1a1),
                            
                            # MID II marks
                            m2q1a=get_col_value(row, col_m2q1a),
                            m2q1b=get_col_value(row, col_m2q1b),
                            m2q2a=get_col_value(row, col_m2q2a),
                            m2q2b=get_col_value(row, col_m2q2b),
                            m2q3a=get_col_value(row, col_m2q3a),
                            m2q3b=get_col_value(row, col_m2q3b),
                            m2qu2=get_col_value(row, col_m2qu2),
                            m2a2=get_col_value(row, col_m2a2),
                        )
                        records_created += 1
                        
                    except Exception as e:
                        print(f"Error in sheet '{current_sheet}': {e}, row: {list(row)}")
                        continue
                
                if records_created > 0:
                    total_records_created += records_created
                    sheets_processed += 1
                    subjects_uploaded.append(f"{current_subject} ({records_created})")
                    print(f"Processed sheet '{current_sheet}': {records_created} records")
                
            except Exception as e:
                print(f"Error processing sheet '{current_sheet}': {e}")
                continue
        
        if process_all_sheets:
            subject_list = ', '.join(subjects_uploaded)
            messages.success(request, f'Successfully uploaded {total_records_created} records from {sheets_processed} sheets: {subject_list} - {semester} ({batch})')
        else:
            messages.success(request, f'Successfully uploaded {total_records_created} records for {subjects_uploaded[0] if subjects_uploaded else "subject"} - {semester} ({batch})')
        
    except Exception as e:
        messages.error(request, f'Error processing file: {str(e)}')
        import traceback
        traceback.print_exc()
    
    return redirect('index')
