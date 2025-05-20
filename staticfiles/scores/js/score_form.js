$(document).ready(function() {
    // Function to update subjects dropdown
    function updateSubjects() {
        var gradeId = $('#id_grade').val();
        var $subjects = $('#id_subject');
        var $scoreType = $('#id_score_type');
        
        if (gradeId) {
            $subjects.prop('disabled', true);
            $.get('/scores/subject/get_subjects/', {grade_id: gradeId}, function(data) {
                $subjects.empty();
                $subjects.append($('<option></option>').val('').text('انتخاب درس'));
                $.each(data, function(index, subject) {
                    $subjects.append($('<option></option>').val(subject.id).text(subject.name));
                });
                $subjects.prop('disabled', false);
            }).fail(function() {
                alert('خطا در دریافت لیست دروس');
                $subjects.prop('disabled', false);
            });
        } else {
            $subjects.empty();
            $subjects.append($('<option></option>').val('').text('انتخاب درس'));
            $scoreType.val('');
        }
    }

    // Function to update classes dropdown
    function updateClasses() {
        var gradeId = $('#id_grade').val();
        var $classes = $('#id_class_obj');
        
        if (gradeId) {
            $classes.prop('disabled', true);
            $.get('/scores/class/get_classes/', {grade_id: gradeId}, function(data) {
                $classes.empty();
                $classes.append($('<option></option>').val('').text('انتخاب کلاس'));
                $.each(data, function(index, class_) {
                    $classes.append($('<option></option>').val(class_.id).text(class_.name));
                });
                $classes.prop('disabled', false);
            }).fail(function() {
                alert('خطا در دریافت لیست کلاس‌ها');
                $classes.prop('disabled', false);
            });
        } else {
            $classes.empty();
            $classes.append($('<option></option>').val('').text('انتخاب کلاس'));
        }
    }

    // Function to update students dropdown
    function updateStudents() {
        var classId = $('#id_class_obj').val();
        var $students = $('#id_user_profile');
        
        if (classId) {
            $students.prop('disabled', true);
            $.get('/scores/student/get_students/', {class_id: classId}, function(data) {
                $students.empty();
                $students.append($('<option></option>').val('').text('انتخاب دانش‌آموز'));
                $.each(data, function(index, student) {
                    $students.append($('<option></option>').val(student.id).text(student.full_name));
                });
                $students.prop('disabled', false);
            }).fail(function() {
                alert('خطا در دریافت لیست دانش‌آموزان');
                $students.prop('disabled', false);
            });
        } else {
            $students.empty();
            $students.append($('<option></option>').val('').text('انتخاب دانش‌آموز'));
        }
    }

    // Event handlers
    $('#id_grade').change(function() {
        updateSubjects();
        updateClasses();
        $('#id_user_profile').empty().append($('<option></option>').val('').text('انتخاب دانش‌آموز'));
    });

    $('#id_class_obj').change(function() {
        updateStudents();
    });

    // Initial updates if values are pre-selected
    if ($('#id_grade').val()) {
        updateSubjects();
        updateClasses();
    }
    if ($('#id_class_obj').val()) {
        updateStudents();
    }
}); 