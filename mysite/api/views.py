import json
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# 간단한 메모리 저장소
ITEMS = {}
NEXT_ID = 1

@csrf_exempt
def item_list(request):
    global NEXT_ID
    if request.method == 'GET':
        # 전체 목록 반환
        return JsonResponse(list(ITEMS.values()), safe=False)

    elif request.method == 'POST':
        # 새 항목 생성
        try:
            payload = json.loads(request.body)
            name = payload.get('name')
            if not name:
                return JsonResponse({'error': 'name 필수'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON'}, status=400)

        item = {'id': NEXT_ID, 'name': name}
        ITEMS[NEXT_ID] = item
        NEXT_ID += 1
        return JsonResponse(item, status=201)

    return HttpResponseNotAllowed(['GET', 'POST'])

@csrf_exempt
def item_detail(request, item_id):
    item = ITEMS.get(item_id)
    if not item:
        return JsonResponse({'error': '존재하지 않는 항목'}, status=404)

    if request.method == 'GET':
        # 단일 조회
        return JsonResponse(item)

    elif request.method == 'PUT':
        # 수정
        try:
            payload = json.loads(request.body)
            name = payload.get('name')
            if not name:
                return JsonResponse({'error': 'name 필수'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '잘못된 JSON'}, status=400)

        item['name'] = name
        return JsonResponse(item)

    elif request.method == 'DELETE':
        # 삭제
        del ITEMS[item_id]
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])