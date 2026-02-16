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
    
    # Get row configuration
    header_row = int(request.POST.get('header_row', 3))
    data_start_row = int(request.POST.get('data_start_row', 4))
    
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
        
        # Column name mappings (case-insensitive, exact matching after cleaning)
        # Specific patterns (with a/b) are checked first, then fallback patterns (without a/b)
        column_patterns_specific = {
            's_no': ['sno', 's.no', 'slno', 'sl.no', 'serialno', 'serial'],
            'regd_no': ['regdno', 'regd.no', 'regno', 'reg.no', 'registration', 'rollno', 'roll.no'],
            'm1q1a': ['m1q1a', 'm1q1(a)', 'mid1q1a', 'mid1q1(a)'],
            'm1q1b': ['m1q1b', 'm1q1(b)', 'mid1q1b', 'mid1q1(b)'],
            'm1q2a': ['m1q2a', 'm1q2(a)', 'mid1q2a', 'mid1q2(a)'],
            'm1q2b': ['m1q2b', 'm1q2(b)', 'mid1q2b', 'mid1q2(b)'],
            'm1q3a': ['m1q3a', 'm1q3(a)', 'mid1q3a', 'mid1q3(a)'],
            'm1q3b': ['m1q3b', 'm1q3(b)', 'mid1q3b', 'mid1q3(b)'],
            'm1qu1': ['m1qu1', 'm1quiz', 'mid1quiz', 'quiz1'],
            'm1a1': ['m1a1', 'm1assignment', 'mid1assignment', 'assignment1'],
            'm2q1a': ['m2q1a', 'm2q1(a)', 'mid2q1a', 'mid2q1(a)'],
            'm2q1b': ['m2q1b', 'm2q1(b)', 'mid2q1b', 'mid2q1(b)'],
            'm2q2a': ['m2q2a', 'm2q2(a)', 'mid2q2a', 'mid2q2(a)'],
            'm2q2b': ['m2q2b', 'm2q2(b)', 'mid2q2b', 'mid2q2(b)'],
            'm2q3a': ['m2q3a', 'm2q3(a)', 'mid2q3a', 'mid2q3(a)'],
            'm2q3b': ['m2q3b', 'm2q3(b)', 'mid2q3b', 'mid2q3(b)'],
            'm2qu2': ['m2qu2', 'm2quiz', 'mid2quiz', 'quiz2'],
            'm2a2': ['m2a2', 'm2assignment', 'mid2assignment', 'assignment2'],
        }
        
        # Fallback patterns: if column is "M1Q1" (no a/b), map to the 'a' variant
        column_patterns_fallback = {
            'm1q1a': ['m1q1', 'mid1q1'],
            'm1q2a': ['m1q2', 'mid1q2'],
            'm1q3a': ['m1q3', 'mid1q3'],
            'm2q1a': ['m2q1', 'mid2q1'],
            'm2q2a': ['m2q2', 'mid2q2'],
            'm2q3a': ['m2q3', 'mid2q3'],
        }
        
        def find_column_index(headers, field_name):
            """Find column index by matching header names - exact matching only"""
            # First, try specific patterns (with a/b suffix)
            patterns = column_patterns_specific.get(field_name, [])
            for idx, header in enumerate(headers):
                if pd.notna(header):
                    # Skip numeric headers
                    try:
                        float(header)
                        continue  # Skip numeric column headers
                    except (ValueError, TypeError):
                        pass
                    
                    header_clean = str(header).lower().strip().replace('_', '').replace('-', '').replace('.', '').replace(' ', '').replace('(', '').replace(')', '')
                    
                    for pattern in patterns:
                        pattern_clean = pattern.replace('.', '').replace('-', '').replace(' ', '').replace('_', '').replace('(', '').replace(')', '')
                        
                        # Exact match only - must be the same after cleaning
                        if header_clean == pattern_clean:
                            print(f"Found '{field_name}' at column {idx}: '{header}' matched specific pattern '{pattern}'")
                            return idx
            
            # If not found, try fallback patterns (without a/b suffix)
            fallback_patterns = column_patterns_fallback.get(field_name, [])
            for idx, header in enumerate(headers):
                if pd.notna(header):
                    # Skip numeric headers
                    try:
                        float(header)
                        continue
                    except (ValueError, TypeError):
                        pass
                    
                    header_clean = str(header).lower().strip().replace('_', '').replace('-', '').replace('.', '').replace(' ', '').replace('(', '').replace(')', '')
                    
                    for pattern in fallback_patterns:
                        pattern_clean = pattern.replace('.', '').replace('-', '').replace(' ', '').replace('_', '').replace('(', '').replace(')', '')
                        
                        if header_clean == pattern_clean:
                            print(f"Found '{field_name}' at column {idx}: '{header}' matched fallback pattern '{pattern}' (no a/b suffix)")
                            return idx
            
            return -1
        
        # Helper function to get value from column
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
                
                # Get headers from header row
                headers = df.iloc[header_row].tolist()
                print(f"\n=== Processing sheet '{current_sheet}' ===")
                print(f"Headers found in row {header_row}: {headers}")
                
                # Auto-detect column indices
                col_sno = find_column_index(headers, 's_no')
                col_regno = find_column_index(headers, 'regd_no')
                col_m1q1a = find_column_index(headers, 'm1q1a')
                col_m1q1b = find_column_index(headers, 'm1q1b')
                col_m1q2a = find_column_index(headers, 'm1q2a')
                col_m1q2b = find_column_index(headers, 'm1q2b')
                col_m1q3a = find_column_index(headers, 'm1q3a')
                col_m1q3b = find_column_index(headers, 'm1q3b')
                col_m1qu1 = find_column_index(headers, 'm1qu1')
                col_m1a1 = find_column_index(headers, 'm1a1')
                col_m2q1a = find_column_index(headers, 'm2q1a')
                col_m2q1b = find_column_index(headers, 'm2q1b')
                col_m2q2a = find_column_index(headers, 'm2q2a')
                col_m2q2b = find_column_index(headers, 'm2q2b')
                col_m2q3a = find_column_index(headers, 'm2q3a')
                col_m2q3b = find_column_index(headers, 'm2q3b')
                col_m2qu2 = find_column_index(headers, 'm2qu2')
                col_m2a2 = find_column_index(headers, 'm2a2')
                
                print(f"\nColumn mapping summary for sheet '{current_sheet}':")
                print(f"  S.No: {col_sno}, Regd No: {col_regno}")
                print(f"  M1: Q1a={col_m1q1a}, Q1b={col_m1q1b}, Q2a={col_m1q2a}, Q2b={col_m1q2b}, Q3a={col_m1q3a}, Q3b={col_m1q3b}")
                print(f"  M1: Qu1={col_m1qu1}, A1={col_m1a1}")
                print(f"  M2: Q1a={col_m2q1a}, Q1b={col_m2q1b}, Q2a={col_m2q2a}, Q2b={col_m2q2b}, Q3a={col_m2q3a}, Q3b={col_m2q3b}")
                print(f"  M2: Qu2={col_m2qu2}, A2={col_m2a2}")
                
                # Validate required columns found
                if col_sno == -1 or col_regno == -1:
                    print(f"Warning: Required columns not found in sheet '{current_sheet}'")
                    print(f"  S.No column: {'Found at ' + str(col_sno) if col_sno != -1 else 'NOT FOUND'}")
                    print(f"  Reg No column: {'Found at ' + str(col_regno) if col_regno != -1 else 'NOT FOUND'}")
                    print(f"  Available headers: {[h for h in headers if pd.notna(h)]}")
                    continue
                
                # Skip to data start row
                df = df.iloc[data_start_row:].reset_index(drop=True)
                
                # Remove rows with empty S.No
                df = df.dropna(subset=[col_sno])
                df = df[df[col_sno] != '']
                
                # Filter out non-numeric S.No
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
                import traceback
                traceback.print_exc()
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
